from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Activity, BudgetItem, Direction


@receiver(pre_delete, sender=Activity)
def refund_budget_on_delete(sender, instance, **kwargs):
    with transaction.atomic():
        budget = BudgetItem.objects.select_for_update().get(pk=instance.budget_item.pk)
        direction = Direction.objects.select_for_update().get(pk=budget.direction.pk)

        budget.remaining_amount += instance.amount
        budget.save(update_fields=['remaining_amount'])

        direction.remaining_amount += instance.amount
        direction.save(update_fields=['remaining_amount'])
