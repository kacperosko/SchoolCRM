from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from apps.authentication import views as authentication_views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', authentication_views.user_login, name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),

    path("user", authentication_views.users, name="crm-users"),
    path("user/<str:user_id>", authentication_views.UserPage.as_view(), name="crm-user-page")
]
