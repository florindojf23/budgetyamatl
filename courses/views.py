from decimal import Decimal
from django.contrib import messages
from django.db.models import Count, Sum, F, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.db.models.functions import Coalesce
from .models import Course, Cohort, Student, Registration
from django.conf import settings
from .forms import StudentForm, RegistrationForm, CourseForm, CohortForm, StudentForm, PaymentForm
from openpyxl import Workbook
from django.utils import timezone
from datetime import datetime
from collections import defaultdict
from datetime import date

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader


def dashboard(request):
    courses = Course.objects.annotate(
        student_count=Count("cohorts__registrations", distinct=True),
        total_paid=Coalesce(
            Sum("cohorts__registrations__amount_paid"),
            Decimal("0.00")
        ),
    )

    total_students = Registration.objects.count()

    total_paid = Registration.objects.aggregate(
        total=Coalesce(Sum("amount_paid"), Decimal("0.00"))
    )["total"]

    total_course_fee = Registration.objects.aggregate(
        total=Coalesce(Sum("course_fee"), Decimal("0.00"))
    )["total"]

    total_registration_fee = Registration.objects.aggregate(
        total=Coalesce(Sum("registration_fee"), Decimal("0.00"))
    )["total"]

    total_expected = total_course_fee + total_registration_fee
    total_balance = total_expected - total_paid

    context = {
        "courses": courses,
        "total_students": total_students,
        "total_paid": total_paid,
        "total_expected": total_expected,
        "total_balance": total_balance,
    }

    return render(request, "courses/dashboard.html", context)

def dashboard2(request):

    # ==========================================
    # 1. SUMMARY CARDS
    # ==========================================

    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_cohorts = Cohort.objects.count()
    total_registrations = Registration.objects.count()

    registrations = Registration.objects.select_related(
        "student", "cohort", "cohort__course"
    )

    expected_revenue = Decimal("0.00")
    total_collected = Decimal("0.00")

    paid_count = 0
    partial_count = 0
    unpaid_count = 0

    for registration in registrations:
        expected_revenue += registration.total_fee
        total_collected += registration.amount_paid or Decimal("0.00")

        if registration.payment_status == "Paid":
            paid_count += 1
        elif registration.payment_status == "Partial":
            partial_count += 1
        else:
            unpaid_count += 1

    outstanding_balance = expected_revenue - total_collected

    # ==========================================
    # 2. REGISTRATIONS BY COURSE
    # ==========================================

    courses = Course.objects.annotate(
        student_count=Count(
            "cohorts__registrations",
            distinct=True
        )
    ).order_by("name")

    course_labels = []
    course_students = []

    for course in courses:
        course_labels.append(course.name)
        course_students.append(course.student_count)

    # ==========================================
    # 3. COURSE FINANCIAL PERFORMANCE
    # ==========================================

    course_performance = []

    for course in courses:

        course_registrations = registrations.filter(
            cohort__course=course
        )

        course_expected = Decimal("0.00")
        course_collected = Decimal("0.00")

        for registration in course_registrations:
            course_expected += registration.total_fee
            course_collected += registration.amount_paid or Decimal("0.00")

        course_performance.append({
            "course": course,
            "students": course.student_count,
            "expected": course_expected,
            "collected": course_collected,
            "balance": course_expected - course_collected,
        })

    # ==========================================
    # 4. MONTHLY PAYMENT COLLECTION
    # ==========================================

    monthly_payments = defaultdict(lambda: Decimal("0.00"))

    recent_payments = []

    for registration in registrations:

        history = registration.payment_history or []

        # Support older registrations without history
        if not history and registration.amount_paid and registration.amount_paid > 0:
            history = [{
                "date": registration.payment_date.strftime("%Y-%m-%d")
                    if registration.payment_date else "",
                "amount": str(registration.amount_paid),
                "method": registration.payment_method or "",
                "notes": registration.notes or "",
            }]

        for index, payment in enumerate(history):

            try:
                payment_date = date.fromisoformat(payment["date"])
                payment_amount = Decimal(str(payment["amount"]))
            except (ValueError, TypeError, KeyError):
                continue

            month_key = payment_date.strftime("%Y-%m")

            monthly_payments[month_key] += payment_amount

            recent_payments.append({
                "student": registration.student,
                "course": registration.cohort.course,
                "registration": registration,
                "date": payment_date,
                "amount": payment_amount,
                "method": payment.get("method", ""),
                "payment_index": index,
            })

    # Sort monthly payments chronologically
    sorted_months = sorted(monthly_payments.keys())

    monthly_labels = [
        date.fromisoformat(month + "-01").strftime("%b %Y")
        for month in sorted_months
    ]

    monthly_values = [
        float(monthly_payments[month])
        for month in sorted_months
    ]

    # Latest 10 payments
    recent_payments.sort(
        key=lambda payment: payment["date"],
        reverse=True
    )

    recent_payments = recent_payments[:10]

    # ==========================================
    # 5. RECENT REGISTRATIONS
    # ==========================================

    recent_registrations = registrations.order_by(
        "-created_at"
    )[:10]

    # ==========================================
    # 6. TEMPLATE CONTEXT
    # ==========================================

    context = {
        "total_students": total_students,
        "total_courses": total_courses,
        "total_cohorts": total_cohorts,
        "total_registrations": total_registrations,

        "expected_revenue": expected_revenue,
        "total_collected": total_collected,
        "outstanding_balance": outstanding_balance,

        "paid_count": paid_count,
        "partial_count": partial_count,
        "unpaid_count": unpaid_count,

        "course_labels": course_labels,
        "course_students": course_students,

        "course_performance": course_performance,

        "monthly_labels": monthly_labels,
        "monthly_values": monthly_values,

        "recent_registrations": recent_registrations,
        "recent_payments": recent_payments,
    }

    return render(request, "courses/dashboard.html", context)


def course_list(request):
    courses = Course.objects.annotate(
        student_count=Count("cohorts__registrations", distinct=True),
        total_paid=Coalesce(Sum("cohorts__registrations__amount_paid"), Decimal("0.00")),
    )

    return render(request, "courses/course_list.html", {"courses": courses})

def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Course successfully created.")
            return redirect("course_list")
    else:
        form = CourseForm()

    return render(
        request,
        "courses/form.html",
        {"form": form, "title": "New Course"},
    )


def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)

        if form.is_valid():
            form.save()
            messages.success(request, "Course successfully updated.")
            return redirect("course_detail", pk=course.pk)
    else:
        form = CourseForm(instance=course)

    return render(
        request,
        "courses/form.html",
        {"form": form, "course": course, "title": "Edit Course"},
    )


def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        course.delete()
        messages.success(request, "Course successfully deleted.")
        return redirect("course_list")

    return render(
        request,
        "courses/course_confirm_delete.html",
        {"course": course},
    )

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)

    cohorts = Cohort.objects.filter(course=course).annotate(
        student_count=Count("registrations", distinct=True),
        total_course_fee=Coalesce(
            Sum("registrations__course_fee"), Decimal("0.00")
        ),
        total_registration_fee=Coalesce(
            Sum("registrations__registration_fee"), Decimal("0.00")
        ),
        total_paid=Coalesce(
            Sum("registrations__amount_paid"), Decimal("0.00")
        ),
    )

    for cohort in cohorts:
        cohort.total_expected = (
            cohort.total_course_fee + cohort.total_registration_fee
        )
        cohort.total_balance = cohort.total_expected - cohort.total_paid

    registrations = Registration.objects.filter(
        cohort__course=course
    ).select_related(
        "student", "cohort", "cohort__course"
    )

    return render(request, "courses/course_detail.html", {
        "course": course,
        "cohorts": cohorts,
        "registrations": registrations,
    })


def course_export_excel(request):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Courses"

    worksheet.append([
        "Code",
        "Course Name",
        "Fee",
        "Status",
        "Students",
    ])

    courses = Course.objects.annotate(
        student_count=Count("cohorts__registrations", distinct=True)
    )

    for course in courses:
        worksheet.append([
            course.code,
            course.name,
            float(course.fee),
            "Active" if course.active else "Inactive",
            course.student_count,
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="courses.xlsx"'

    workbook.save(response)

    return response


def cohort_list(request):
    cohorts = Cohort.objects.select_related("course").annotate(
        student_count=Count("registrations", distinct=True),
        total_paid=Coalesce(
            Sum("registrations__amount_paid"),
            Decimal("0.00")
        ),
    )

    return render(
        request,
        "courses/cohort_list.html",
        {"cohorts": cohorts}
    )


def cohort_create(request):
    if request.method == "POST":
        form = CohortForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Cohort successfully created.")
            return redirect("cohort_list")
    else:
        form = CohortForm()

    return render(
        request,
        "courses/form.html",
        {"form": form, "title": "New Cohort"},
    )


def cohort_update(request, pk):
    cohort = get_object_or_404(Cohort, pk=pk)

    if request.method == "POST":
        form = CohortForm(request.POST, instance=cohort)

        if form.is_valid():
            form.save()
            messages.success(request, "Cohort successfully updated.")
            return redirect("cohort_detail", pk=cohort.pk)
    else:
        form = CohortForm(instance=cohort)

    return render(
        request,
        "courses/form.html",
        {
            "form": form,
            "cohort": cohort,
            "title": "Edit Cohort",
        },
    )


def cohort_delete(request, pk):
    cohort = get_object_or_404(Cohort, pk=pk)

    if request.method == "POST":
        cohort.delete()
        messages.success(request, "Cohort successfully deleted.")
        return redirect("cohort_list")

    return render(
        request,
        "courses/cohort_confirm_delete.html",
        {"cohort": cohort},
    )

def cohort_detail(request, pk):
    cohort = get_object_or_404(
        Cohort.objects.select_related("course"),
        pk=pk
    )

    registrations = Registration.objects.filter(
        cohort=cohort
    ).select_related("student")

    summary = registrations.aggregate(
        student_count=Count("id"),
        course_fee=Coalesce(
            Sum("course_fee"), Decimal("0.00")
        ),
        registration_fee=Coalesce(
            Sum("registration_fee"), Decimal("0.00")
        ),
        amount_paid=Coalesce(
            Sum("amount_paid"), Decimal("0.00")
        ),
    )

    expected = summary["course_fee"] + summary["registration_fee"]
    balance = expected - summary["amount_paid"]

    return render(request, "courses/cohort_detail.html", {
        "cohort": cohort,
        "registrations": registrations,
        "summary": summary,
        "expected": expected,
        "balance": balance,
    })

def cohort_export_excel(request):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Cohorts"

    worksheet.append([
        "Course",
        "Cohort",
        "Start Date",
        "End Date",
        "Registration",
        "Students",
    ])

    cohorts = Cohort.objects.select_related("course").annotate(
        student_count=Count("registrations", distinct=True)
    )

    for cohort in cohorts:
        worksheet.append([
            cohort.course.name if cohort.course else "",
            cohort.name,
            cohort.start_date,
            cohort.end_date,
            "Open" if cohort.registration_open else "Closed",
            cohort.student_count,
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="cohorts.xlsx"'

    workbook.save(response)

    return response


def registration_create(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            registration = form.save()

            messages.success(request, "Registration successfully created.")

            return redirect("registration_list")

    else:
        form = RegistrationForm()

    return render(
        request,
        "courses/form.html",
        {"form": form, "title": "New Registration"},
    )

def registration_list(request):
    registrations = Registration.objects.select_related(
        "student", "cohort", "cohort__course"
    )

    course_id = request.GET.get("course")
    cohort_id = request.GET.get("cohort")

    if course_id:
        registrations = registrations.filter(cohort__course_id=course_id)

    if cohort_id:
        registrations = registrations.filter(cohort_id=cohort_id)

    courses = Course.objects.filter(active=True)
    cohorts = Cohort.objects.all()

    context = {
        "registrations": registrations,
        "courses": courses,
        "cohorts": cohorts,
    }

    return render(request, "courses/registo_list.html", context)


def registration_update(request, pk):
    registration = get_object_or_404(Registration, pk=pk)

    if request.method == "POST":
        form = RegistrationForm(request.POST, instance=registration)

        if form.is_valid():
            form.save()
            messages.success(request, "Registration successfully updated.")
            return redirect("registration_list")
    else:
        form = RegistrationForm(instance=registration)

    return render(request, "courses/form.html", {
        "form": form,
        "registration": registration,
        "title": "Edit Registration",
    })


def registration_delete(request, pk):
    registration = get_object_or_404(Registration, pk=pk)

    if request.method == "POST":
        registration.delete()
        messages.success(request, "Registration successfully deleted.")
        return redirect("registration_list")

    return render(request, "courses/registration_confirm_delete.html", {
        "registration": registration,
    })

def registration_detail(request, pk):
    registration = get_object_or_404(
        Registration.objects.select_related(
            "student",
            "cohort",
            "cohort__course"
        ),
        pk=pk
    )

    payment_history = registration.payment_history or []

    # If old registration has a payment but no payment history,
    # automatically show that payment as Payment 1.
    if not payment_history and registration.amount_paid and registration.amount_paid > 0:
        payment_history = [{
            "date": registration.payment_date.strftime("%Y-%m-%d")
                if registration.payment_date else "",
            "amount": str(registration.amount_paid),
            "method": registration.payment_method or "",
            "notes": registration.notes or "",
        }]

    return render(
        request,
        "courses/registration_detail.html",
        {
            "registration": registration,
            "payment_history": payment_history,
        }
    )

def registration_export_excel(request):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Registrations"

    worksheet.append([
        "Registration ID",
        "Student",
        "Registration No",
        "Course",
        "Cohort",
        "Course Fee",
        "Registration Fee",
        "Total Fee",
        "Amount Paid",
        "Balance",
        "Payment Status",
        "Payment Method",
        "Payment Date",
        "Notes",
    ])

    registrations = Registration.objects.select_related(
        "student",
        "cohort",
        "cohort__course",
    ).order_by("id")

    for registration in registrations:
        worksheet.append([
            registration.id,
            registration.student.full_name if registration.student else "",
            registration.student.reg_no if registration.student else "",
            registration.cohort.course.name if registration.cohort and registration.cohort.course else "",
            registration.cohort.name if registration.cohort else "",
            float(registration.course_fee or 0),
            float(registration.registration_fee or 0),
            float(registration.total_fee),
            float(registration.amount_paid or 0),
            float(registration.balance),
            registration.payment_status,
            registration.payment_method,
            registration.payment_date,
            registration.notes,
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="registrations.xlsx"'

    workbook.save(response)

    return response


def student_list(request):
    students = Student.objects.all()

    return render(
        request,
        "courses/student_list.html",
        {"students": students}
    )


def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Student successfully created.")
            return redirect("student_list")
    else:
        form = StudentForm()

    return render(
        request,
        "courses/form.html",
        {"form": form, "title": "New Student"},
    )


def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)

        if form.is_valid():
            form.save()
            messages.success(request, "Student successfully updated.")
            return redirect("student_list")
    else:
        form = StudentForm(instance=student)

    return render(
        request,
        "courses/form.html",
        {
            "form": form,
            "student": student,
            "title": "Edit Student",
        },
    )

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        student.delete()
        messages.success(request, "Student successfully deleted.")
        return redirect("student_list")

    return render(
        request,
        "courses/student_confirm_delete.html",
        {"student": student},
    )

def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    registrations = Registration.objects.filter(
        student=student
    ).select_related("cohort", "cohort__course")

    return render(request, "courses/student_detail.html", {
        "student": student,
        "registrations": registrations,
    })

def student_export_excel(request):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Students"

    worksheet.append([
        "Registration No",
        "Full Name",
        "Sexo",
        "Semester",
        "Study Program",
        "Birth Date",
        "Email",
        "Phone",
        "Address",
    ])

    students = Student.objects.all().order_by("id")

    for student in students:
        worksheet.append([
            student.reg_no,
            student.full_name,
            student.sex,
            student.education_semester or "",
            student.study_program,
            student.birth_date,
            student.email,
            student.phone,
            student.address,
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="Lista_students.xlsx"'

    workbook.save(response)

    return response

def Registration_serverside_data(request):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))

    search_value = request.GET.get("search[value]", "").strip()

    order_column_index = request.GET.get("order[0][column]")
    order_direction = request.GET.get("order[0][dir]", "asc")

    column_map = {
        0: "student__full_name",
        1: "cohort__course__name",
        2: "cohort__name",
        3: "course_fee",
        4: "amount_paid",
        5: "amount_paid",
        6: "amount_paid",
        7: "payment_date",
    }

    queryset = Registration.objects.select_related(
        "student",
        "cohort",
        "cohort__course",
    )

    records_total = queryset.count()

    if search_value:
        search_filter = (
            Q(student__full_name__icontains=search_value) |
            Q(student__reg_no__icontains=search_value) |
            Q(cohort__name__icontains=search_value) |
            Q(cohort__course__name__icontains=search_value) |
            Q(payment_method__icontains=search_value) |
            Q(notes__icontains=search_value)
        )

        queryset = queryset.filter(search_filter)

    records_filtered = queryset.count()

    if order_column_index is not None:
        column_index = int(order_column_index)
        column_name = column_map.get(column_index, "id")

        if order_direction == "desc":
            column_name = f"-{column_name}"

        queryset = queryset.order_by(column_name)

    queryset = queryset[start:start + length]

    data = []

    for registration in queryset:
        data.append({
        "id": registration.id,
        "student_id": registration.student.id,
        "student": registration.student.full_name,
        "course": registration.cohort.course.name if registration.cohort and registration.cohort.course else "",
        "cohort": registration.cohort.name if registration.cohort else "",
        "total_fee": float(registration.total_fee),
        "amount_paid": float(registration.amount_paid or 0),
        "balance": float(registration.balance),
        "payment_status": registration.payment_status,
        "payment_date": registration.payment_date.strftime("%Y-%m-%d") if registration.payment_date else "",
    })

    return JsonResponse({
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": data,
    })


def Student_serverside_data(request):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))

    search_value = request.GET.get("search[value]", "").strip()

    order_column_index = request.GET.get("order[0][column]")
    order_direction = request.GET.get("order[0][dir]", "asc")

    column_map = {
    0: "reg_no",
    1: "full_name",
    2: "sex",
    3: "education_semester",
    4: "study_program",
    5: "birth_date",
    6: "email",
    7: "phone",
}

    queryset = Student.objects.all()

    records_total = queryset.count()

    if search_value:
        search_filter = (
            Q(reg_no__icontains=search_value) |
            Q(full_name__icontains=search_value) |
            Q(study_program__icontains=search_value) |
            Q(email__icontains=search_value) |
            Q(phone__icontains=search_value) |
            Q(address__icontains=search_value)
        )

        queryset = queryset.filter(search_filter)

    records_filtered = queryset.count()

    if order_column_index is not None:
        column_index = int(order_column_index)
        column_name = column_map.get(column_index, "id")

        if order_direction == "desc":
            column_name = f"-{column_name}"

        queryset = queryset.order_by(column_name)

    queryset = queryset[start:start + length]

    data = []

    for student in queryset:
        data.append({
            "id": student.id,
            "reg_no": student.reg_no,
            "full_name": student.full_name,
            "sex": student.get_sex_display() if student.sex else "",
            "education_semester": student.education_semester or "",
            "study_program": student.study_program,
            "birth_date": student.birth_date.strftime("%Y-%m-%d") if student.birth_date else "",
            "email": student.email,
            "phone": student.phone,
            "address": student.address,

        })

    return JsonResponse({
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": data,
    })

def Course_serverside_data(request):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))

    search_value = request.GET.get("search[value]", "").strip()

    order_column_index = request.GET.get("order[0][column]")
    order_direction = request.GET.get("order[0][dir]", "asc")

    column_map = {
        0: "code",
        1: "name",
        2: "fee",
        3: "active",
        4: "student_count",
    }

    queryset = Course.objects.annotate(
        student_count=Count("cohorts__registrations", distinct=True)
    )

    records_total = queryset.count()

    if search_value:
        search_filter = (
            Q(code__icontains=search_value) |
            Q(name__icontains=search_value)
        )

        queryset = queryset.filter(search_filter)

    records_filtered = queryset.count()

    if order_column_index is not None:
        column_index = int(order_column_index)
        column_name = column_map.get(column_index, "id")

        if order_direction == "desc":
            column_name = f"-{column_name}"

        queryset = queryset.order_by(column_name)

    queryset = queryset[start:start + length]

    data = []

    for course in queryset:
        data.append({
            "id": course.id,
            "code": course.code,
            "name": course.name,
            "fee": float(course.fee),
            "active": "Ativu" if course.active else "La Ativu",
            "student_count": course.student_count,
        })

    return JsonResponse({
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": data,
    })


def Cohort_serverside_data(request):
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))

    search_value = request.GET.get("search[value]", "").strip()

    order_column_index = request.GET.get("order[0][column]")
    order_direction = request.GET.get("order[0][dir]", "asc")

    column_map = {
        0: "course__name",
        1: "name",
        2: "start_date",
        3: "end_date",
        4: "registration_open",
        5: "student_count",
    }

    queryset = Cohort.objects.select_related("course").annotate(
        student_count=Count("registrations", distinct=True)
    )

    records_total = queryset.count()

    if search_value:
        search_filter = (
            Q(course__name__icontains=search_value) |
            Q(course__code__icontains=search_value) |
            Q(name__icontains=search_value)
        )

        queryset = queryset.filter(search_filter)

    records_filtered = queryset.count()

    if order_column_index is not None:
        column_index = int(order_column_index)
        column_name = column_map.get(column_index, "id")

        if order_direction == "desc":
            column_name = f"-{column_name}"

        queryset = queryset.order_by(column_name)

    queryset = queryset[start:start + length]

    data = []

    for cohort in queryset:
        data.append({
            "id": cohort.id,
            "course": cohort.course.name if cohort.course else "",
            "name": cohort.name,
            "start_date": cohort.start_date.strftime("%Y-%m-%d") if cohort.start_date else "",
            "end_date": cohort.end_date.strftime("%Y-%m-%d") if cohort.end_date else "",
            "registration_open": "Aberto" if cohort.registration_open else "Taka",
            "student_count": cohort.student_count,
        })

    return JsonResponse({
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": data,
    })

def registration_receipt_pdf(request, pk):
    registration = get_object_or_404(
        Registration.objects.select_related(
            "student",
            "cohort",
            "cohort__course",
        ),
        pk=pk,
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="payment_receipt_{registration.id}.pdf"'
    )

    # -----------------------------------------------------
    # A5 LANDSCAPE
    # -----------------------------------------------------
    pdf = canvas.Canvas(
        response,
        pagesize=landscape(A5),
    )

    pdf.setTitle(f"RECEIPT - {registration.student}")

    page_width, page_height = landscape(A5)

    # A5 is divided into 2 receipts SIDE-BY-SIDE
    receipt_width = page_width / 2

    logo_path = (
        settings.BASE_DIR
        / "courses"
        / "static"
        / "courses"
        / "images"
        / "yamatl.jpg"
    )

    def draw_receipt(x_left):

        # -------------------------------------------------
        # Receipt dimensions
        # -------------------------------------------------
        margin = 12

        left = x_left + margin
        right = x_left + receipt_width - margin
        bottom = 15
        top = page_height - 15

        width = right - left
        height = top - bottom

        # -------------------------------------------------
        # Outer border
        # -------------------------------------------------
        pdf.setStrokeColor(colors.black)
        pdf.setLineWidth(0.8)

        pdf.rect(
            left,
            bottom,
            width,
            height,
        )

        # -------------------------------------------------
        # Header
        # -------------------------------------------------
        header_height = 55
        header_y = top - header_height

        pdf.line(
            left,
            header_y,
            right,
            header_y,
        )

        # -------------------------------------------------
        # LEFT LOGO
        # -------------------------------------------------
        try:
            pdf.drawImage(
                ImageReader(str(logo_path)),
                left + 5,
                top - 45,
                width=58,
                height=36,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass

        # -------------------------------------------------
        # RIGHT LOGO
        # -------------------------------------------------
        try:
            pdf.drawImage(
                ImageReader(str(logo_path)),
                right - 63,
                top - 45,
                width=58,
                height=36,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------
        pdf.setFont("Helvetica-Bold", 10)

        pdf.drawCentredString(
            (left + right) / 2,
            top - 29,
            "PAYMENT RECEIPT",
        )

        # -------------------------------------------------
        # Content positions
        # -------------------------------------------------
        label_x = left + 8
        colon_x = left + 92
        value_x = left + 102

        row_y = header_y - 20
        row_height = 25

        # -------------------------------------------------
        # Program
        # -------------------------------------------------
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(
            label_x,
            row_y,
            "Program",
        )

        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(colon_x, row_y, ":")

        pdf.drawString(
            value_x,
            row_y,
            registration.cohort.course.name,
        )

        row_y -= row_height

        # -------------------------------------------------
        # Participant Name
        # -------------------------------------------------
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(
            label_x,
            row_y,
            "Participant Name",
        )

        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(colon_x, row_y, ":")

        # Keep long names inside the receipt
        participant_name = registration.student.full_name

        if len(participant_name) > 40:
            participant_name = participant_name[:40] + "..."

        pdf.drawString(
            value_x,
            row_y,
            participant_name,
        )

        row_y -= row_height

        # -------------------------------------------------
        # Total Course Fee + Registration
        # -------------------------------------------------
        pdf.setFont("Helvetica-Bold", 7.5)

        pdf.drawString(
            label_x,
            row_y,
            "Total Course Fee +",
        )

        pdf.drawString(
            label_x,
            row_y - 10,
            "Registration",
        )

        pdf.setFont("Helvetica", 7.5)

        pdf.drawString(
            colon_x,
            row_y,
            ":",
        )

        pdf.drawString(
            value_x,
            row_y,
            f"$ {registration.total_fee:,.2f}",
        )

        row_y -= 31

        # -------------------------------------------------
        # Amount Paid
        # -------------------------------------------------
        pdf.setFont("Helvetica-Bold", 7.5)

        pdf.drawString(
            label_x,
            row_y,
            "Amount Paid",
        )

        pdf.setFont("Helvetica", 7.5)

        pdf.drawString(
            colon_x,
            row_y,
            ":",
        )

        pdf.drawString(
            value_x,
            row_y,
            f"$ {(registration.amount_paid or Decimal('0.00')):,.2f}",
        )

        row_y -= row_height

        # -------------------------------------------------
        # Remaining Balance
        # -------------------------------------------------
        pdf.setFont("Helvetica-Bold", 7.5)

        pdf.drawString(
            label_x,
            row_y,
            "Remaining Balance",
        )

        pdf.setFont("Helvetica", 7.5)

        pdf.drawString(
            colon_x,
            row_y,
            ":",
        )

        pdf.drawString(
            value_x,
            row_y,
            f"$ {registration.balance:,.2f}",
        )

        row_y -= row_height

        # -------------------------------------------------
        # Date of Payment
        # -------------------------------------------------
        pdf.setFont("Helvetica-Bold", 7.5)

        pdf.drawString(
            label_x,
            row_y,
            "Date of Payment",
        )

        pdf.setFont("Helvetica", 7.5)

        pdf.drawString(
            colon_x,
            row_y,
            ":",
        )

        payment_date = (
            registration.payment_date.strftime("%d / %m / %Y")
            if registration.payment_date
            else "____ / ____ / ______"
        )

        pdf.drawString(
            value_x,
            row_y,
            payment_date,
        )

        # -------------------------------------------------
        # Bottom separator
        # -------------------------------------------------
        bottom_section_y = bottom + 58

        pdf.line(
            left,
            bottom_section_y,
            right,
            bottom_section_y,
        )

        # -------------------------------------------------
        # Received By
        # -------------------------------------------------
        pdf.setFont("Helvetica-Bold", 7.5)

        pdf.drawString(
            label_x,
            bottom_section_y - 20,
            "Received by",
        )

        pdf.setFont("Helvetica", 7.5)

        pdf.drawString(
            colon_x,
            bottom_section_y - 20,
            ":",
        )

        pdf.line(
            value_x,
            bottom_section_y - 22,
            right - 8,
            bottom_section_y - 22,
        )

        # -------------------------------------------------
        # Signature
        # -------------------------------------------------
        pdf.setFont("Helvetica-Bold", 7.5)

        pdf.drawString(
            label_x,
            bottom_section_y - 40,
            "Signature",
        )

        pdf.setFont("Helvetica", 7.5)

        pdf.drawString(
            colon_x,
            bottom_section_y - 40,
            ":",
        )

        pdf.line(
            value_x,
            bottom_section_y - 42,
            right - 35,
            bottom_section_y - 42,
        )

    # -----------------------------------------------------
    # LEFT RECEIPT
    # -----------------------------------------------------
    draw_receipt(0)

    # -----------------------------------------------------
    # RIGHT RECEIPT
    # -----------------------------------------------------
    draw_receipt(receipt_width)

    # -----------------------------------------------------
    # CENTER CUTTING LINE
    # -----------------------------------------------------
    pdf.setDash(3, 3)
    pdf.setStrokeColor(colors.grey)
    pdf.setLineWidth(0.5)

    pdf.line(
        receipt_width,
        8,
        receipt_width,
        page_height - 8,
    )

    pdf.setDash()

    # -----------------------------------------------------
    # Finish PDF
    # -----------------------------------------------------
    pdf.save()

    return response


def payment_receipt_pdf(request, pk, payment_index):
    registration = get_object_or_404(
        Registration.objects.select_related(
            "student",
            "cohort",
            "cohort__course",
        ),
        pk=pk,
    )

    history = registration.payment_history or []

    # Check payment number
    if payment_index < 0 or payment_index >= len(history):
        messages.error(request, "Payment record not found.")
        return redirect("registration_detail", pk=registration.pk)

    payment = history[payment_index]

    # Current payment amount
    payment_amount = Decimal(str(payment.get("amount", "0.00")))

    # Calculate total paid up to this payment
    total_paid_at_payment = Decimal("0.00")

    for index, item in enumerate(history):
        if index <= payment_index:
            total_paid_at_payment += Decimal(
                str(item.get("amount", "0.00"))
            )

    remaining_balance = registration.total_fee - total_paid_at_payment

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="payment_{payment_index + 1}_'
        f'receipt_{registration.id}.pdf"'
    )

    pdf = canvas.Canvas(response, pagesize=landscape(A5))

    page_width, page_height = landscape(A5)
    receipt_width = page_width / 2

    logo_path = (
        settings.BASE_DIR
        / "courses"
        / "static"
        / "courses"
        / "images"
        / "yamatl.jpg"
    )

    def draw_receipt(x_left):

        margin = 12
        left = x_left + margin
        right = x_left + receipt_width - margin
        bottom = 15
        top = page_height - 15

        width = right - left

        # Border
        pdf.setStrokeColor(colors.black)
        pdf.setLineWidth(0.8)
        pdf.rect(left, bottom, width, top - bottom)

        # Header
        header_height = 55
        header_y = top - header_height

        pdf.line(left, header_y, right, header_y)

        # Left logo
        try:
            pdf.drawImage(
                ImageReader(str(logo_path)),
                left + 5,
                top - 45,
                width=58,
                height=36,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass

        # Right logo
        try:
            pdf.drawImage(
                ImageReader(str(logo_path)),
                right - 63,
                top - 45,
                width=58,
                height=36,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass

        # Title
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawCentredString(
            (left + right) / 2,
            top - 29,
            "PAYMENT RECEIPT"
        )

        label_x = left + 8
        colon_x = left + 92
        value_x = left + 102

        row_y = header_y - 18
        row_height = 22

        # Payment number
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(label_x, row_y, "Payment No.")
        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(colon_x, row_y, ":")
        pdf.drawString(
            value_x,
            row_y,
            f"Payment {payment_index + 1}"
        )

        # Program
        row_y -= row_height

        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(label_x, row_y, "Program")

        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(colon_x, row_y, ":")
        pdf.drawString(
            value_x,
            row_y,
            registration.cohort.course.name
        )

        # Participant
        row_y -= row_height

        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(label_x, row_y, "Participant Name")

        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(colon_x, row_y, ":")

        participant_name = registration.student.full_name

        if len(participant_name) > 27:
            participant_name = participant_name[:27] + "..."

        pdf.drawString(
            value_x,
            row_y,
            participant_name
        )

        # This payment
        row_y -= row_height

        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(label_x, row_y, "This Payment")

        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(colon_x, row_y, ":")
        pdf.drawString(
            value_x,
            row_y,
            f"$ {payment_amount:,.2f}"
        )

        # Total paid
        row_y -= row_height

        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(label_x, row_y, "Total Paid")

        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(colon_x, row_y, ":")
        pdf.drawString(
            value_x,
            row_y,
            f"$ {total_paid_at_payment:,.2f}"
        )

        # Remaining balance
        row_y -= row_height

        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(label_x, row_y, "Remaining Balance")

        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(colon_x, row_y, ":")

        pdf.drawString(
            value_x,
            row_y,
            f"$ {remaining_balance:,.2f}"
        )

        # Payment date
        row_y -= row_height

        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(label_x, row_y, "Date of Payment")

        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(colon_x, row_y, ":")

        payment_date = payment.get("date", "")

        if payment_date:
            try:
                formatted_date = datetime.strptime(
                    payment_date,
                    "%Y-%m-%d"
                ).strftime("%d / %m / %Y")
            except ValueError:
                formatted_date = payment_date
        else:
            formatted_date = "____ / ____ / ______"

        pdf.drawString(
            value_x,
            row_y,
            formatted_date
        )

        # Payment method
        row_y -= row_height

        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(label_x, row_y, "Payment Method")

        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(colon_x, row_y, ":")

        pdf.drawString(
            value_x,
            row_y,
            payment.get("method", "")
        )

        # Bottom section
        bottom_section_y = bottom + 58

        pdf.line(
            left,
            bottom_section_y,
            right,
            bottom_section_y
        )

        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(
            label_x,
            bottom_section_y - 20,
            "Received by"
        )

        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(
            colon_x,
            bottom_section_y - 20,
            ":"
        )

        pdf.line(
            value_x,
            bottom_section_y - 22,
            right - 8,
            bottom_section_y - 22
        )

        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawString(
            label_x,
            bottom_section_y - 40,
            "Signature"
        )

        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(
            colon_x,
            bottom_section_y - 40,
            ":"
        )

        pdf.line(
            value_x,
            bottom_section_y - 42,
            right - 35,
            bottom_section_y - 42
        )

    # Two identical receipts on A5 landscape
    draw_receipt(0)
    draw_receipt(receipt_width)

    # Cutting line
    pdf.setDash(3, 3)
    pdf.setStrokeColor(colors.grey)
    pdf.setLineWidth(0.5)

    pdf.line(
        receipt_width,
        8,
        receipt_width,
        page_height - 8
    )

    pdf.setDash()

    pdf.save()

    return response


def add_payment(request, pk):
    registration = get_object_or_404(
        Registration.objects.select_related(
            "student",
            "cohort",
            "cohort__course",
        ),
        pk=pk
    )

    if request.method == "POST":
        form = PaymentForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data["amount"]
            payment_method = form.cleaned_data["payment_method"]
            payment_date = form.cleaned_data["payment_date"]
            notes = form.cleaned_data["notes"]

            remaining = registration.balance

            if amount > remaining:
                messages.error(
                    request,
                    f"Payment cannot be greater than the remaining balance "
                    f"of ${remaining:,.2f}."
                )
            else:
                history = registration.payment_history or []

                history.append({
                    "date": payment_date.strftime("%Y-%m-%d"),
                    "amount": str(amount),
                    "method": payment_method,
                    "notes": notes,
                })

                registration.payment_history = history

                # Increase total amount paid
                registration.amount_paid = (
                    registration.amount_paid or Decimal("0.00")
                ) + amount

                # Keep latest payment information
                registration.payment_method = payment_method
                registration.payment_date = payment_date

                registration.save()

                messages.success(
                    request,
                    f"Payment of ${amount:,.2f} successfully added."
                )

                return redirect(
                    "registration_detail",
                    pk=registration.pk
                )
    else:
        form = PaymentForm(
            initial={
                "payment_date": timezone.localdate()
            }
        )

    return render(
        request,
        "courses/payment_form.html",
        {
            "form": form,
            "registration": registration,
        }
    )


def edit_payment(request, pk, payment_index):
    registration = get_object_or_404(
        Registration.objects.select_related(
            "student",
            "cohort",
            "cohort__course",
        ),
        pk=pk
    )

    history = registration.payment_history or []

    if payment_index < 0 or payment_index >= len(history):
        messages.error(request, "Payment record not found.")
        return redirect("registration_detail", pk=registration.pk)

    payment = history[payment_index]

    if request.method == "POST":
        form = PaymentForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data["amount"]
            payment_method = form.cleaned_data["payment_method"]
            payment_date = form.cleaned_data["payment_date"]
            notes = form.cleaned_data["notes"]

            # Calculate total of all other payments
            other_payments = Decimal("0.00")

            for index, item in enumerate(history):
                if index != payment_index:
                    other_payments += Decimal(str(item.get("amount", "0.00")))

            new_total = other_payments + amount

            if new_total > registration.total_fee:
                messages.error(
                    request,
                    f"Payment total cannot exceed "
                    f"${registration.total_fee:,.2f}."
                )
            else:
                # Update ONLY this payment
                history[payment_index] = {
                    "date": payment_date.strftime("%Y-%m-%d"),
                    "amount": str(amount),
                    "method": payment_method,
                    "notes": notes,
                }

                registration.payment_history = history

                # Recalculate total paid
                registration.amount_paid = new_total

                # Keep latest payment information
                registration.payment_method = payment_method
                registration.payment_date = payment_date

                registration.save()

                messages.success(
                    request,
                    f"Payment {payment_index + 1} successfully updated."
                )

                return redirect(
                    "registration_detail",
                    pk=registration.pk
                )

    else:
        form = PaymentForm(
            initial={
                "amount": payment.get("amount", "0.00"),
                "payment_method": payment.get("method", ""),
                "payment_date": payment.get("date", ""),
                "notes": payment.get("notes", ""),
            }
        )

    return render(
        request,
        "courses/payment_form.html",
        {
            "form": form,
            "registration": registration,
            "payment_index": payment_index,
            "editing_payment": True,
        }
    )