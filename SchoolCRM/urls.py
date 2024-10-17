"""SchoolCRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.authentication.forms import MySetPasswordForm
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings


from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

urlpatterns = [
    path('password-reset/', PasswordResetView.as_view(template_name='auth/auth-recover-pwd.html'), name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='auth/auth-confirm-reset-password.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='auth/auth-recover-reset-pwd.html', form_class=MySetPasswordForm), name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(template_name='auth/auth-success-reset-password.html'), name='password_reset_complete'),

    path('warsztatownia/', admin.site.urls),
    path("", include("apps.authentication.urls")),
    path("", include("apps.crm.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.crm.views.custom_404'
handler500 = 'apps.crm.views.custom_500'
