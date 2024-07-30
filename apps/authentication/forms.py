from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.forms import ModelForm
from django.forms.widgets import TextInput
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.core.mail import send_mail
from SchoolCRM.settings import SITE_URL, EMAIL_HOST_USER

UserModel = get_user_model()


class MySetPasswordForm(SetPasswordForm):

    def send_email(self, user):
        send_mail(
            subject="Twoje has\u0142o zosta\u0142o zmienione",
            message=f"Hej {user.first_name},\n\n\ndostajesz tego maila poniewa\u017C"
                    f" Twoje has\u0142o na {SITE_URL} zosta\u0142o zmienione.\n\nJe\u015Bli nie zmienia\u0142e\u015B/a\u015B has\u0142a niezw\u0142ocznie skontaktuj si\u0119 z administratorem strony",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

    def save(self, commit=True):
        if commit:
            self.send_email(self.user)
        super(MySetPasswordForm, self).save(commit=commit)


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        widgets = {
            'avatar_color': TextInput(attrs={'type': 'color'}),
        }
