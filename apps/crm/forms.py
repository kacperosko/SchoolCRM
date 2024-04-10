from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class PersonForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone_number = forms.CharField(required=False)
    # birth_date = forms.DateField(required=False)


class LessonForm(forms.Form):
    startTime = forms.TimeField()
    endTime = forms.TimeField()
    lessonDate = forms.DateField()
    originalDate = forms.DateField()
    lessonId = forms.CharField()
    status = forms.CharField()
    isAdjustment = forms.BooleanField(required=False)

class LessonCreateForm(forms.Form):
    startTime = forms.TimeField()
    endTime = forms.TimeField()
    lessonDate = forms.DateField()
    repeat = forms.CharField()
    description = forms.CharField()
    end_series = forms.DateField(required=False)
    teacher = forms.CharField()


class LessonPlanForm(forms.Form):
    lessonId = forms.CharField()
    status = forms.CharField()
    isAdjustment = forms.BooleanField(required=False)


class StudentPersonForm(forms.Form):
    person = forms.CharField()
    relationship_type = forms.CharField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(required=False)