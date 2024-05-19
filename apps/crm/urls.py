from django.urls import path, include
from apps.crm import views as crm_views
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', crm_views.user_login, name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path("", crm_views.CRMHomePage.as_view(), name="crm-home"),
    path("students", crm_views.students, name="crm-students"),
    path("students/new", crm_views.create_student, name="crm-student-create"),
    path("students/<str:student_id>", crm_views.StudentPage.as_view(), name="crm-students"),
    path("students/<str:student_id>/<str:student_person_id>/delete", crm_views.StudentPersonDelete.as_view(), name="crm-student-person-delete"),
    path("students/<str:student_id>/student-person/add", crm_views.StudentPersonCreate.as_view(), name="crm-student-person-delete"),
    path("students/<str:student_id>/<str:lesson_id>", crm_views.lesson_page, name="crm-lesson-page"),
    path("contacts", crm_views.contacts, name="crm-contacts"),
    path("contacts/new", crm_views.CreateContact.as_view(), name="crm-contact-create"),
    path("contacts/<str:contact_id>", crm_views.ContactPage.as_view(), name="crm-contacts-page"),
    path("calendar", crm_views.calendar, name="crm-calendar"),


    path("crm_api/create-note", crm_views.create_note, name="crm-create_note"),

    path('notifications/', crm_views.get_notifications, name='get_notifications'),
    path('notifications/read/<int:notification_id>/', crm_views.mark_notification_as_read, name='mark_notification_as_read'),

    path("user", crm_views.UserPage.as_view(), name="crm-user-page")
    # path("<path:path>", crm_views.DynamicHTMLView.as_view(), name="dynamic-html"),
    # defaults.page_not_found(request, exception, template_name='404.html')
]

