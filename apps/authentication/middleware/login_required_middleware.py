from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings


def login_exempt(view):
    view.login_exempt = True
    return view


class LoginRequiredMiddleware:
    password_reset_urls = ['/password-reset/', '/password-reset/done/', '/password-reset-complete/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):

        # Check if the request is for a static file
        if request.path.startswith(settings.STATIC_URL):
            return

        if request.path in self.password_reset_urls or request.path.startswith('/password-reset-confirm/'):
            return

        if getattr(view_func, 'login_exempt', False) and not request.user.is_authenticated:
            return

        if request.user.is_authenticated:
            if request.path == '/login/':
                return redirect("/student")
            return

        return login_required(view_func)(request, *view_args, **view_kwargs)
