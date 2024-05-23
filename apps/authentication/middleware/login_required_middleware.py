from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


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
        print(request.path)

        if request.path in self.password_reset_urls or request.path.startswith('/password-reset-confirm/'):
            print("path in password urls")
            return

        print('login_exempt', getattr(view_func, 'login_exempt', False))
        if getattr(view_func, 'login_exempt', False) and not request.user.is_authenticated:
            print("not authenticated")
            return

        if request.user.is_authenticated:
            print(request.path)
            if request.path == '/login/':
                return redirect("/student")
            return

        return login_required(view_func)(request, *view_args, **view_kwargs)
