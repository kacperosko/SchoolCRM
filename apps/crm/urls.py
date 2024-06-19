from django.urls import path, include
from apps.crm import views as crm_views
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, permission_required


urlpatterns = [
    # path('login/', crm_views.user_login, name='login'),
    # path('logout', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path("", crm_views.CRMHomePage.as_view(), name="crm-home"),

    path("student", crm_views.students, name="crm-students"),
    path("student/new", crm_views.create_student, name="crm-student-create"),
    # path("student/new", permission_required('crm.add_student', login_url='/')(crm_views.create_student), name="crm-student-create"),
    path("student/edit/<str:student_id>", crm_views.edit_student, name="crm-student-create"),
    path("student/<str:student_id>", crm_views.StudentPage.as_view(), name="crm-students"),
    path("student/<str:student_id>/<str:student_person_id>/delete", crm_views.StudentPersonDelete.as_view(), name="crm-student-person-delete"),
    path("student/<str:student_id>/student-person/add", crm_views.StudentPersonCreate.as_view(), name="crm-student-person-delete"),
    path("student/<str:student_id>/<str:lesson_id>", crm_views.lesson_page, name="crm-lesson-page"),

    path("person", crm_views.contacts, name="crm-contacts"),
    path("person/new", crm_views.create_contact, name="crm-contact-create"),
    path("person/edit/<str:person_id>", crm_views.edit_person, name="crm-contact-create"),
    path("person/<str:contact_id>", crm_views.ContactPage.as_view(), name="crm-contacts-page"),
    path("calendar", crm_views.calendar, name="crm-calendar"),

    path("location", crm_views.locations, name="crm-locations"),
    path("location/new", crm_views.LocationCreate.as_view(), name="crm-LocationCreate"),
    path("location/<str:location_id>", crm_views.LocationPage.as_view(), name="crm-LocationPage"),



    path("crm_api/get-lessons/<str:student_id>", crm_views.get_student_lessons, name="crm-create_note"),
    path("crm_api/create-note", crm_views.create_note, name="crm-create_note"),

    path('crm_api/notifications/', crm_views.get_notifications, name='get_notifications'),
    path('crm_api/notifications/read/<int:notification_id>/', crm_views.mark_notification_as_read, name='mark_notification_as_read'),

    path('crm_api/watch/<str:mode>/<str:model_name>/<int:record_id>/', crm_views.watch_record, name='watch_record'),


    # path("<path:path>", crm_views.DynamicHTMLView.as_view(), name="dynamic-html"),
    # defaults.page_not_found(request, exception, template_name='404.html')
]

