from django.shortcuts import render
from .middleware.login_required_middleware import login_exempt
from .forms import UserCreationForm, LoginForm
from .models import User
from apps.crm.models import Lesson, Student
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
                login(request, user)
                next_url = request.GET.get("next", "/student")
                return redirect(next_url)
            else:
                message = 'Nazwa u\u017Cytkownika lub has\u0142o s\u0105 niepoprawne'
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

    return render(request, 'auth/users.html', {'users': users_all})


class UserPage(View):
    @staticmethod
    def get(request, *args, **kwargs):
        context = {}

        try:
            user_id = kwargs.get('user_id')
            user = User.objects.get(pk=user_id)
            context['user'] = user

            lessons_with_teacher = Lesson.objects.filter(teacher_id=user_id)
            student_ids = lessons_with_teacher.values_list('student_id', flat=True).distinct()
            students = Student.objects.filter(id__in=student_ids)
            context['students'] = students


        except Exception as e:
            print(e)
        return render(request, 'auth/user-profile.html', context)

    @staticmethod
    def post(request, *args, **kwargs):
        pass
