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
    first_name = forms.CharField(label='Imię')
    last_name = forms.CharField(label='Nazwisko')
    email = forms.EmailField(required=False, label='Email')
    phone_number = forms.CharField(required=False, label='Telefon', max_length=16)


class StudentForm(forms.Form):
    first_name = forms.CharField(label='Imię')
    last_name = forms.CharField(label='Nazwisko')
    email = forms.EmailField(required=False, label='Email')
    phone_number = forms.CharField(required=False, label='Telefon', max_length=16)
    birth_date = forms.DateField(required=False, label='Data urodzin', widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt--2'}))


class LessonForm(forms.Form):
    startTime = forms.TimeField()
    lessonDuration = forms.IntegerField()
    lessonDate = forms.DateField()
    originalDate = forms.DateField()
    lessonId = forms.CharField()
    status = forms.CharField()
    isAdjustment = forms.BooleanField(required=False)


class LessonCreateForm(forms.Form):
    startTime = forms.TimeField()
    lessonDuration = forms.IntegerField()
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
    phone = forms.CharField(required=False)


class LocationForm(forms.Form):
    name = forms.CharField(label='Nazwa')
    country = forms.CharField(label='Kraj', initial='Polska')
    city = forms.CharField(label='Miasto')
    street = forms.CharField(label='Ulica')
    postal_code = forms.CharField(label='Kod pocztowy', max_length=6)
