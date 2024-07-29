from django.urls import path, include
from apps.crm import views as crm_views
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, permission_required


urlpatterns = [
    path("", crm_views.crmHomePage, name="crm-home"),

    path("delete/<str:record_id>", crm_views.delete_record, name="crm-home"),
    path("<str:model_name>/edit/<str:record_id>", crm_views.upsert_record, name="crm-insert_record"),
    path("<str:model_name>/new", crm_views.upsert_record, name="crm-create-record"),

    path("student", crm_views.all_students, name="crm-students"),
    path("student/<str:student_id>", crm_views.StudentPage.as_view(), name="crm-students"),
    path("student/<str:student_id>/student-person/add", crm_views.StudentPersonCreate.as_view(), name="crm-student-person-delete"),
    path("student/<str:student_id>/lesson-series", crm_views.view_student_lesson_series, name="crm-student-view_student_lesson_series"),

    path("person", crm_views.view_contacts, name="crm-contacts"),
    path("person/<str:person_id>", crm_views.view_person, name="crm-contacts-page"),
    path("calendar", crm_views.calendar, name="crm-calendar"),

    path("location", crm_views.all_locations, name="crm-locations"),
    # path("location/new", crm_views.LocationCreate.as_view(), name="crm-LocationCreate"),
    path("<str:model_name>/new", crm_views.upsert_record, name="crm-LocationCreate"),
    path("location/<str:location_id>", crm_views.LocationPage.as_view(), name="crm-LocationPage"),



    path("crm_api/get-lessons/<str:student_id>", crm_views.get_student_lessons, name="crm-create_note"),
    path("crm_api/create-note", crm_views.upsert_note, name="crm-create_note"),
    path("crm_api/delete-note", crm_views.delete_note, name="crm-create_note"),

    path('crm_api/notifications/', crm_views.get_notifications, name='get_notifications'),
    path('crm_api/notifications/read/<int:notification_id>/', crm_views.mark_notification_as_read, name='mark_notification_as_read'),

    path('crm_api/watch/<str:mode>/<str:record_id>/', crm_views.watch_record, name='watch_record'),


    # path("<path:path>", crm_views.DynamicHTMLView.as_view(), name="dynamic-html"),
    # defaults.page_not_found(request, exception, template_name='404.html')
]

