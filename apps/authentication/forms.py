from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.forms import ModelForm
from django.forms.widgets import TextInput


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
