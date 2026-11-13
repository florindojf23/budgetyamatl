from django.db import models
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class YearBudget(models.Model):
    year = models.IntegerField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2)

    def save(self, *args, **kwargs):
        # On create, set remaining_amount = total_amount if empty
        if not self.pk and not self.remaining_amount:
            self.remaining_amount = self.total_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Year {self.year} - Total: {self.total_amount}, Remaining: {self.remaining_amount}"


class Direction(models.Model):
    name = models.CharField(max_length=200)
    year_budget = models.ForeignKey(YearBudget, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2)

    def save(self, *args, **kwargs):
        # On create, set remaining_amount = total_amount if empty
        if not self.pk and not self.remaining_amount:
            self.remaining_amount = self.total_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - Total: {self.total_amount}, Remaining: {self.remaining_amount}"


class BudgetItem(models.Model):
    ITEM_CHOICES = [
        ('salary', 'Salários e Vencimentos'),
        ('goods', 'Bens e Serviços Correntes'),
        ('transfer', 'Transferência'),
        ('capital', 'Capital Menor'),
    ]

    direction = models.ForeignKey(Direction, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=20, choices=ITEM_CHOICES)
    initial_amount = models.DecimalField(max_digits=15, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2)

    def save(self, *args, **kwargs):
        # On create, set remaining_amount = initial_amount if empty
        if not self.pk and not self.remaining_amount:
            self.remaining_amount = self.initial_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_item_type_display()} - {self.direction.name} | Remaining: {self.remaining_amount}"


class Activity(models.Model):
    budget_item = models.ForeignKey(BudgetItem, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()

    def save(self, *args, **kwargs):
        with transaction.atomic():

            # ========================
            # EDIT MODE
            # ========================
            if self.pk:
                old = Activity.objects.select_related(
                    'budget_item__direction'
                ).get(pk=self.pk)

                # RETURN OLD MONEY
                old_budget = BudgetItem.objects.select_for_update().get(pk=old.budget_item.pk)
                old_direction = Direction.objects.select_for_update().get(pk=old.budget_item.direction.pk)

                old_budget.remaining_amount += old.amount
                old_budget.save(update_fields=['remaining_amount'])

                old_direction.remaining_amount += old.amount
                old_direction.save(update_fields=['remaining_amount'])

            # ========================
            # NEW / UPDATED VALUES
            # ========================
            new_budget = BudgetItem.objects.select_for_update().get(pk=self.budget_item.pk)
            new_direction = Direction.objects.select_for_update().get(pk=new_budget.direction.pk)

            # VALIDATION
            if self.amount > new_budget.remaining_amount:
                raise ValidationError("Not enough remaining budget!")

            # SUBTRACT NEW MONEY
            new_budget.remaining_amount -= self.amount
            new_budget.save(update_fields=['remaining_amount'])

            new_direction.remaining_amount -= self.amount
            new_direction.save(update_fields=['remaining_amount'])

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():

            # ALWAYS RELOAD FRESH INSTANCE
            activity = Activity.objects.select_related(
                'budget_item__direction'
            ).get(pk=self.pk)

            budget = BudgetItem.objects.select_for_update().get(pk=activity.budget_item.pk)
            direction = Direction.objects.select_for_update().get(pk=activity.budget_item.direction.pk)

            # REFUND MONEY
            budget.remaining_amount += activity.amount
            budget.save(update_fields=['remaining_amount'])

            direction.remaining_amount += activity.amount
            direction.save(update_fields=['remaining_amount'])

            super(Activity, self).delete(*args, **kwargs)

    def __str__(self):
        return f"{self.name} | {self.budget_item.get_item_type_display()} | {self.amount}"


@receiver(pre_delete, sender=Activity)
def refund_activity_budget(sender, instance, **kwargs):
    from django.db import transaction

    with transaction.atomic():
        budget = BudgetItem.objects.select_for_update().get(pk=instance.budget_item.pk)
        direction = Direction.objects.select_for_update().get(pk=budget.direction.pk)

        budget.remaining_amount += instance.amount
        budget.save(update_fields=['remaining_amount'])

        direction.remaining_amount += instance.amount
        direction.save(update_fields=['remaining_amount'])


