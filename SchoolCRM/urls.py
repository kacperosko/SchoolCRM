from django.contrib import admin
from django.urls import path, include
from apps.authentication.forms import MySetPasswordForm
from django.urls import path, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve


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
    # re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    # re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.crm.views.views_general.custom_404'
handler500 = 'apps.crm.views.views_general.custom_500'
