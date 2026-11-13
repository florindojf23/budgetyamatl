from decimal import Decimal
from django.db import models
from django.utils import timezone


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, unique=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - ${self.fee}"


class Cohort(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="cohorts")
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    registration_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.course.name} - {self.name}"


class Student(models.Model):
    SEX_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
    ]
    reg_no = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=200)
    sex = models.CharField(max_length=10,choices=SEX_CHOICES,blank=True,)
    education_semester = models.PositiveIntegerField(null=True, blank=True)
    study_program = models.CharField(max_length=200, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.reg_no} - {self.full_name}"


class Registration(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("Cash", "Cash"),
        ("Bank Transfer", "Bank Transfer"),
        ("Mobile Payment", "Mobile Payment"),
    ]

    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="registrations")
    cohort = models.ForeignKey(Cohort, on_delete=models.PROTECT, related_name="registrations")
    course_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("2.50"))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    payment_history = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.full_name} - {self.cohort}"

    @property
    def course(self):
        return self.cohort.course

    @property
    def total_fee(self):
        course_fee = self.course_fee or Decimal("0.00")
        registration_fee = self.registration_fee or Decimal("0.00")
        return course_fee + registration_fee

    @property
    def balance(self):
        amount_paid = self.amount_paid or Decimal("0.00")
        return self.total_fee - amount_paid

    @property
    def payment_status(self):
        amount_paid = self.amount_paid or Decimal("0.00")

        if amount_paid <= 0:
            return "Unpaid"
        if amount_paid < self.total_fee:
            return "Partial"
        return "Paid"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new and self.cohort_id:
            self.course_fee = self.cohort.course.fee

        # Automatically create the first payment history
        if is_new and self.amount_paid and self.amount_paid > 0:
            self.payment_history = [{
                "date": self.payment_date.strftime("%Y-%m-%d")
                    if self.payment_date else "",
                "amount": str(self.amount_paid),
                "method": self.payment_method or "",
                "notes": self.notes or "",
            }]

        super().save(*args, **kwargs)
