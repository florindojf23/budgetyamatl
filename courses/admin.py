from django.contrib import admin

from .models import (Course,Cohort,Student,Registration,)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = ["code","name","fee","active",
    ]

    list_filter = [
        "active",
    ]

    search_fields = [
        "code",
        "name",
    ]


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = [
        "name","course","start_date","end_date","registration_open",
    ]

    list_filter = [
        "course","registration_open",
    ]

    search_fields = [
        "name","course__name",
    ]
    date_hierarchy = "start_date"

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = [
        "reg_no","full_name","education_semester","study_program","phone","email",
    ]

    search_fields = [
        "reg_no","full_name","phone","email",
    ]

    list_filter = [
        "study_program","education_semester",
    ]


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):

    list_display = [
        "student",
        "course_name",
        "cohort",
        "course_fee",
        "registration_fee",
        "total_fee_display",
        "amount_paid",
        "balance_display",
        "payment_status_display",
        "payment_method",
        "payment_date",
    ]

    list_filter = [
        "cohort__course",
        "cohort",
        "payment_method",
        "payment_date",
    ]

    search_fields = [
        "student__reg_no",
        "student__full_name",
    ]

    readonly_fields = [
        "course_fee",
        "total_fee_display",
        "balance_display",
        "payment_status_display",
    ]

    @admin.display(
        description="Course"
    )
    def course_name(self, obj):

        if not obj.cohort_id:
            return "-"

        return obj.cohort.course.name

    @admin.display(
        description="Total Fee"
    )
    def total_fee_display(self, obj):

        if not obj.course_fee:
            return "-"

        return obj.total_fee

    @admin.display(
        description="Balance"
    )
    def balance_display(self, obj):

        if not obj.course_fee:
            return "-"

        return obj.balance

    @admin.display(
        description="Status"
    )
    def payment_status_display(self, obj):

        if not obj.course_fee:
            return "-"

        return obj.payment_status

        