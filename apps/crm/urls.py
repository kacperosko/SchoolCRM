from django.urls import path, include
from apps.crm import views as crm_views
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, permission_required

urlpatterns = [
    path("", crm_views.crm_home_page, name="crm-home"),

    path("delete/<str:record_id>", crm_views.delete_record, name="crm-home"),
    path("<str:model_name>/edit/<str:record_id>", crm_views.upsert_record, name="crm-insert_record"),
    path("<str:model_name>/new", crm_views.upsert_record, name="crm-create-record"),

    path("report", crm_views.view_reports, name="crm-reports"),
    path("calendar", crm_views.calendar, name="crm-calendar"),
    path("<str:model_name>/", crm_views.view_all, name="crm-view-all"),
    path("crm_api/records/all", crm_views.get_all_records, name="crm-view-all"),

    path("student", crm_views.all_students,
         name="crm-students"),

# ścieżka URL dla strony szczegółowej rekordu student
    path("student/<str:student_id>", crm_views.view_student, name="crm-view_student"),

    path("student/<str:student_id>/student-person/add", crm_views.StudentPersonCreate.as_view(),
         name="crm-student-person-add"),

    path("person", crm_views.all_persons, name="crm-person"),
    path("person/<str:person_id>", crm_views.view_person, name="crm-view_person"),

    path("location", crm_views.all_locations, name="crm-locations"),
    path("location/<str:location_id>", crm_views.view_location, name="crm-view_location"),

    path("group", crm_views.all_groups, name="crm-groups"),
    path("group/<str:group_id>", crm_views.view_group, name="crm-view_group"),

    path("attendancelist/<str:attendance_list_id>", crm_views.view_attendance_list, name="crm-view_attendance_list"),
    path("invoice/<str:invoice_id>", crm_views.view_invoice, name="crm-view_invoice"),

    path("report/paid-student-lessons-month", crm_views.view_student_report, name="crm-student-report"),
    path("report/paid-student-lessons-in-group-month", crm_views.view_students_in_group_report,
         name="crm-student-group-report"),

    path("crm_api/get-lessons/<str:record_id>", crm_views.get_student_group_lessons,
         name="crm-get_student_group_lessons"),
    path("crm_api/create-note", crm_views.upsert_note, name="crm-create_note"),
    path("crm_api/delete-note", crm_views.delete_note, name="crm-delet_note"),

    path('crm_api/notifications/', crm_views.get_notifications, name='get_notifications'),
    path('crm_api/notifications/read/<str:notification_id>/', crm_views.mark_notification_as_read,
         name='mark_notification_as_read'),

    path('crm_api/watch/<str:mode>/<str:record_id>/', crm_views.watch_record, name='watch_record'),

    path('crm_api/save-attendance-list/', crm_views.save_attendance_list_student, name='crm_save_attendance_list_student'),
    path('crm_api/create-lesson/', crm_views.create_lesson, name='crm_create_lesson'),
    path('crm_api/edit-lesson/', crm_views.edit_lesson, name='crm_edit_lesson'),
    path('crm_api/update_status/', crm_views.update_status, name='crm_update_status'),

    path('crm_api/create-attendance-list/', crm_views.create_attendance_list_student, name='crm_create_attendance_list'),
]


