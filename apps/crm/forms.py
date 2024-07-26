from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import Location, Person, Student
import importlib


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class PersonForm(forms.ModelForm):
    title = "Kontakt"

    class Meta:
        model = Person
        fields = "__all__"
        exclude = ('id',)

    first_name = forms.CharField(label='Imię')
    last_name = forms.CharField(label='Nazwisko')
    email = forms.EmailField(required=False, label='Email')
    phone = forms.CharField(required=False, label='Telefon', max_length=16)


class StudentForm(forms.ModelForm):
    title = "Student"

    class Meta:
        model = Student
        fields = "__all__"
        exclude = ('id', 'created_by', 'modified_by', 'created_date', 'modified_date')

    first_name = forms.CharField(label='Imię')
    last_name = forms.CharField(label='Nazwisko')
    email = forms.EmailField(required=False, label='Email')
    phone = forms.CharField(required=False, label='Telefon', max_length=16)
    birthdate = forms.DateField(required=False, label='Data urodzin',
                                widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt--2'})
                                # input_formats=["%d-%M-%Y"]
                                )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     birthdate = self.fields['birthdate']
    #     if birthdate:
    #         print('birthdate', birthdate.strptime('21-10-2023', '%d-%m-%Y'))
    #         # self.fields['birthdate'] = birthdate.strftime('%d-%m-%Y')


class LessonForm(forms.Form):
    startTime = forms.TimeField()
    lessonDuration = forms.IntegerField()
    lessonDate = forms.DateField()
    originalDate = forms.DateField()
    lessonId = forms.CharField()
    status = forms.CharField()
    isAdjustment = forms.BooleanField(required=False)
    teacher = forms.CharField()
    location = forms.CharField()


class LessonCreateForm(forms.Form):
    startTime = forms.TimeField()
    lessonDuration = forms.IntegerField()
    lessonDate = forms.DateField()
    repeat = forms.CharField()
    description = forms.CharField()
    end_series = forms.DateField(required=False)
    teacher = forms.CharField()
    location = forms.CharField()


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


class LocationForm(forms.ModelForm):
    title = "Lokalizacja"

    class Meta:
        model = Location
        fields = "__all__"
        exclude = ('id',)

    name = forms.CharField(label='Nazwa')
    country = forms.CharField(label='Kraj', initial='Polska')
    city = forms.CharField(label='Miasto')
    street = forms.CharField(label='Ulica')
    postal_code = forms.CharField(label='Kod pocztowy', max_length=6)


def get_form_class(form_name):
    """
    Returns the form class based on its name.

    :param form_name: The name of the form class to retrieve.
    :return: The form class.
    """
    try:
        # Pobieranie bieżącego modułu
        module = importlib.import_module(__name__)
        form_class = getattr(module, form_name)
    except (ImportError, AttributeError):
        raise ValueError(f"Form class '{form_name}' not found.")

    return form_class
