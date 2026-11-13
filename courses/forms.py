from django import forms
from .models import *
from decimal import Decimal


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "reg_no",
            "full_name",
            "sex",
            "education_semester",
            "study_program",
            "birth_date",
            "email",
            "phone",
            "address",
        ]

        widgets = {
            "birth_date": forms.DateInput(
                attrs={
                    "class": "form-control datepicker",
                    "placeholder": "YYYY-MM-DD",
                    "autocomplete": "off",
                }
            ),
        }


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ["student", "cohort", "registration_fee", "amount_paid", "payment_method", "payment_date", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Find students whose registration balance is $0.00
        paid_student_ids = [
            reg.student_id for reg in Registration.objects.select_related("cohort", "cohort__course")
            if reg.balance <= 0
        ]

        # Hide fully paid students when creating a new registration
        if not self.instance.pk:
            self.fields["student"].queryset = Student.objects.exclude(id__in=paid_student_ids)

        # Display Registration No. and Student Name
        self.fields["student"].label_from_instance = lambda obj: f"{obj.reg_no} - {obj.full_name}"


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["code", "name", "fee", "active"]

class CohortForm(forms.ModelForm):
    class Meta:
        model = Cohort
        fields = [
            "course",
            "name",
            "start_date",
            "end_date",
            "registration_open",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control datepicker",
                    "placeholder": "YYYY-MM-DD",
                    "autocomplete": "off",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control datepicker",
                    "placeholder": "YYYY-MM-DD",
                    "autocomplete": "off",
                }
            ),
        }


class PaymentForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01")
    )

    payment_method = forms.ChoiceField(
        choices=Registration.PAYMENT_METHOD_CHOICES
    )

    payment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "class": "form-control datepicker",
            "placeholder": "YYYY-MM-DD",
            "autocomplete": "off",
        })
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 2,
            "class": "form-control"
        })
    )
