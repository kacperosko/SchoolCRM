from django.shortcuts import render
from .middleware.login_required_middleware import login_exempt
from .forms import UserCreationForm, LoginForm, UserAvatarForm
from .models import User
from apps.crm.models import Student, Event
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
from apps.service_helper import check_permission, is_admin, custom_404, check_is_admin


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
                sleep(4)
        else:
            message = form.errors
    else:
        form = LoginForm()
    return render(request, 'auth/auth-sign-in.html', {'form': form, 'message': message})


@check_is_admin
def users(request):
    users_all = None
    try:
        users_all = User.objects.all().order_by("-first_name")
    except Exception as e:
        messages.error(request, e)

    return render(request, 'auth/users.html', {'users': users_all})


class UserPage(View):
    @staticmethod
    def get(request, *args, **kwargs):
        context = {}
        user_id = kwargs.get('user_id')

        if user_id != request.user.id and not is_admin(request):
            return custom_404(request, 'Brak uprawnień do wyświetlenia tej strony')

        try:
            user = User.objects.get(pk=user_id)
            context['user'] = user

            lessons_with_teacher = Event.objects.filter(teacher__id=user_id)
            student_ids = lessons_with_teacher.values_list('lesson_definition__student_id', flat=True).distinct()
            students = Student.objects.filter(id__in=student_ids).order_by('first_name')
            context['students'] = students

        except User.DoesNotExist as e:
            messages.error(request, 'Nie znaleziono uzytkownika z takim id: {user_id}'.format(user_id=user_id))
            return redirect("/user")
        except Exception as e:
            messages.error(request, 'Wystąpił błąd: {e}'.format(e=e))
            return redirect("/user")
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
        return redirect(f'/user/view/{request.user.id}')
