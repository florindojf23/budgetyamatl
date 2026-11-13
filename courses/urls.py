from django.urls import path
from . import views


urlpatterns = [

    path("dashboard/", views.dashboard2, name="dashboard2"),
    path("", views.dashboard, name="dashboard"),

    # Courses
    path("courses/", views.course_list, name="course_list"),
    path("courses/add/", views.course_create, name="course_create"),
    path("courses/<int:pk>/edit/", views.course_update, name="course_update"),
    path("courses/<int:pk>/delete/", views.course_delete, name="course_delete"),
    path("courses/<int:pk>/", views.course_detail, name="course_detail"),
    path("courses/export-excel/", views.course_export_excel, name="course_export_excel"),

    # Cohorts
    path("batches/", views.cohort_list, name="cohort_list"),
    path("batches/add/", views.cohort_create, name="cohort_create"),
    path("batches/<int:pk>/edit/", views.cohort_update, name="cohort_update"),
    path("batches/<int:pk>/delete/", views.cohort_delete, name="cohort_delete"),
    path("batches/<int:pk>/", views.cohort_detail, name="cohort_detail"),
    path("batches/export-excel/", views.cohort_export_excel, name="cohort_export_excel"),

    # Students
    path("students/", views.student_list, name="student_list"),
    path("students/add/", views.student_create, name="student_create"),
    path("students/<int:pk>/edit/", views.student_update, name="student_update"),
    path("students/<int:pk>/delete/", views.student_delete, name="student_delete"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),
    path("students/export-excel/", views.student_export_excel, name="student_export_excel"),
    

    # Registrations
    path("registrations/", views.registration_list, name="registration_list"),
    path("registrations/add/", views.registration_create, name="registration_create"),
    path("registrations/<int:pk>/edit/", views.registration_update, name="registration_update"),
    path("registrations/<int:pk>/delete/", views.registration_delete, name="registration_delete"),
    path("registrations/<int:pk>/", views.registration_detail, name="registration_detail"),
    path("registrations/export-excel/", views.registration_export_excel, name="registration_export_excel"),
    path("registrations/<int:pk>/receipt/", views.registration_receipt_pdf, name="registration_receipt_pdf"),
    path("registrations/<int:pk>/add-payment/",views.add_payment,name="add_payment"),
    path("registrations/<int:pk>/payment/<int:payment_index>/edit/",views.edit_payment,name="edit_payment"),
    path("registrations/<int:pk>/payment/<int:payment_index>/receipt/",views.payment_receipt_pdf,name="payment_receipt_pdf"),
    


    # Registration DataTables
    path("registrations/server-data/",views.Registration_serverside_data,name="Registration_serverside_data"),
    path("students/server-data/", views.Student_serverside_data, name="Student_serverside_data"),
    path("courses/server-data/", views.Course_serverside_data, name="Course_serverside_data"),
    path("cohorts/server-data/", views.Cohort_serverside_data, name="Cohort_serverside_data"),

]