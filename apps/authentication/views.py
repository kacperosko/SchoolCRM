from django.shortcuts import render
from .middleware.login_required_middleware import login_exempt
from .forms import UserCreationForm, LoginForm, UserAvatarForm
from .models import User
from apps.crm.models import Lesson, Student
from django.contrib.auth import authenticate, login, logout
from time import sleep
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from PIL import Image
import base64
from django.core.files.base import ContentFile
from io import BytesIO
import os


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
                next_url = request.GET.get("next", "/")
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
        users_all = User.objects.all().order_by("-first_name")
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
        try:
            cropped_image_data = request.POST.get('cropped_image')

            format, imgstr = cropped_image_data.split(';base64,')

            image_data = ContentFile(base64.b64decode(imgstr), name='profile_picture.png')
            image = Image.open(image_data)

            if image.mode == 'RGBA':
                image = image.convert('RGB')

            image_io = BytesIO()
            image.save(image_io, format='JPEG')

            file_name = f'profilPic{request.user.id}.jpg'
            image_file = ContentFile(image_io.getvalue(), name=file_name)

            if request.user.user_avatar:
                try:
                    existing_file_path = request.user.user_avatar.path
                    if os.path.isfile(existing_file_path):
                        os.remove(existing_file_path)
                except Exception as e:
                    print(f"Nie udało się usunąć istniejącego pliku: {e}")

            request.user.user_avatar.save(file_name, image_file, save=True)

        except Exception as e:
            messages.error(request, f"Bład podczas zapisywania zdjęcia: {e}")
        return redirect(f'/user/{request.user.id}')
