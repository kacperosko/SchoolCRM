from django.shortcuts import render
from .middleware.login_required_middleware import login_exempt
from .forms import UserCreationForm, LoginForm
from .models import User
from django.contrib.auth import authenticate, login, logout
from time import sleep
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.contrib.auth.decorators import permission_required


@login_exempt
def user_login(request):
    message = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                print('authenticated', user)
                login(request, user)
                next_url = request.GET.get("next", "/student")
                return redirect(next_url)
            else:
                message = 'Nazwa użytkownika lub hasło są niepoprawne'
                print(message)
                sleep(4)
        else:
            message = form.errors
    else:
        form = LoginForm()
    return render(request, 'auth/auth-sign-in.html', {'form': form, 'message': message})


@permission_required('crm.view_user', raise_exception=False, login_url="/")
def users(request):
    users_all = None
    try:
        users_all = User.objects.all().order_by("-last_name").order_by("-first_name")
    except Exception as e:
        print(e)

    return render(request, 'app/users.html', {'users': users_all})


class UserPage(View):
    @staticmethod
    def get(request, *args, **kwargs):
        user_id = kwargs['user_id']
        try:
            user = User.objects.get(pk=user_id)
        except Exception as e:
            print(e)
        return render(request, 'app/user-profile.html', {'user': user})

    @staticmethod
    def post(request, *args, **kwargs):
        pass
