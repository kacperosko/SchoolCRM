from django import forms
from django.contrib.auth.models import User
from apps.authentication.models import Group as AuthGroup
from django.forms import ModelForm
from django.test import override_settings
from django.core.exceptions import ValidationError

from .models import Location, Person, Student, StudentPerson, GroupStudent, Group, AttendanceList, Invoice, AttendanceListStudent, LessonDefinition, Event, InvoiceItem
from apps.authentication.models import User
import importlib
from django.utils import timezone as dj_timezone
import datetime


class PersonForm(forms.ModelForm):
    @staticmethod
    def get_name():
        return "Kontakt"

    class Meta:
        model = Person
        fields = "__all__"
        exclude = ('id',)

    first_name = forms.CharField(label='Imi\u0119')
    last_name = forms.CharField(label='Nazwisko')
    email = forms.EmailField(required=False, label='Email')
    phone = forms.CharField(required=False, label='Telefon', max_length=16)



class StudentForm(forms.ModelForm):
    @staticmethod
    def get_name():
        return "Uczeń"

    class Meta:
        model = Student
        fields = "__all__"
        exclude = ('id', 'created_by', 'modified_by', 'created_date', 'modified_date')

    first_name = forms.CharField(label='Imi\u0119')
    last_name = forms.CharField(label='Nazwisko')
    email = forms.EmailField(required=False, label='Email')
    phone = forms.CharField(required=False, label='Telefon', max_length=16)
    birthdate = forms.DateField(required=False, label='Data urodzin',
                                widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt--2'})
                                )



class LessonModuleForm(forms.Form):
    startTime = forms.TimeField()
    lessonDuration = forms.IntegerField()
    lessonDate = forms.DateField()
    originalDate = forms.DateField()
    lessonId = forms.CharField()
    status = forms.CharField()
    isAdjustment = forms.BooleanField(required=False)
    teacher = forms.CharField()
    location = forms.CharField()


class LessonCreateForm(forms.ModelForm):
    class Meta:
        model = LessonDefinition
        fields = ['lesson_date', 'start_time', 'duration', 'description', 'series_end_date', 'is_series', 'student', 'group', 'teacher', 'location']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'lesson_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'series_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'duration': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'is_series': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
            'group': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
        }


class EditLessonForm(forms.ModelForm):
    # Dodajemy dodatkowe pole spoza modelu:
    edit_mode = forms.ChoiceField(choices=[
        ('single', 'single'),
        ('series', 'series')
    ], required=True)
    is_seried = forms.BooleanField(required=False)

    class Meta:
        model = Event
        fields = [
            'start_time',
            'duration',
            'event_date',
            'status',
            'teacher',
            'location',
            'description',
        ]

    # Dodatkowe ustawienia formatów dla daty i godziny:
    start_time = forms.TimeField(input_formats=["%H:%M"])
    event_date = forms.DateField(input_formats=["%Y-%m-%d"])

    def clean_duration(self):
        data = self.cleaned_data['duration']
        return int(data)

    def save(self, commit=True):
        event = super().save(commit=False)

        # Wyliczamy end_time na podstawie start_time i duration
        from datetime import datetime, timedelta

        # tworzymy datetime pomocniczy do dodania minut
        dummy_date = datetime.combine(event.event_date, event.start_time)
        end_dt = dummy_date + timedelta(minutes=event.duration)
        event.end_time = end_dt.time()

        if commit:
            event.save()
        return event



class LessonPlanForm(forms.Form):
    lessonId = forms.CharField()
    status = forms.CharField()
    isAdjustment = forms.BooleanField(required=False)


class StudentPersonAddForm(forms.Form):
    person = forms.CharField()
    relationship_type = forms.CharField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)


class StudentpersonForm(forms.ModelForm):
    @staticmethod
    def get_name():
        return "Relacja ze Studentem"

    class Meta:
        model = StudentPerson
        fields = "__all__"
        exclude = ('id',)

    def __init__(self, *args, **kwargs):
        # user = kwargs.pop('user','')
        super(StudentpersonForm, self).__init__(*args, **kwargs)
        self.fields['student'].label = 'Student'
        self.fields['student'].disabled = True
        self.fields['person'].label = 'Kontakt'
        self.fields['person'].disabled = True
        self.fields['relationship_type'].label = 'Relacja'


class LocationForm(forms.ModelForm):
    @staticmethod
    def get_name():
        return "Lokalizacja"

    class Meta:
        model = Location
        fields = "__all__"
        exclude = ('id',)

    name = forms.CharField(label='Nazwa')
    country = forms.CharField(label='Kraj', initial='Polska')
    city = forms.CharField(label='Miasto')
    street = forms.CharField(label='Ulica')
    postal_code = forms.CharField(label='Kod pocztowy', max_length=6)


class UserForm(forms.ModelForm):

    @staticmethod
    def get_name():
        return "Nauczyciel"

    class Meta:
        model = User
        fields = "__all__"
        exclude = ('id', 'password', 'is_active', 'is_staff', 'is_superuser', 'staff', 'admin', 'user_permissions', 'last_login', 'user_avatar', 'groups')


    group = forms.ModelChoiceField(queryset=AuthGroup.objects.all(), label='Rola', required=True)
    email = forms.CharField(label='Email', disabled=True)
    first_name = forms.CharField(label='Imi\u0119')
    last_name = forms.CharField(label='Nazwisko')
    phone = forms.CharField(label='Telefon', max_length=20, required=False)
    avatar_color = forms.CharField(label='Kolor awatara', widget=forms.TextInput(attrs={'type': 'color'}))

    def save(self, commit=True):
        instance = super(UserForm, self).save(commit=False)
        new_group = self.cleaned_data.get('group')

        is_administrator = new_group and new_group.name == "Administrator"
        instance.is_superuser = is_administrator
        instance.admin = is_administrator
        instance.staff = is_administrator

        if commit:
            instance.save()

            instance.groups.clear()
            if new_group:
                instance.groups.add(new_group)

        return instance

    def __init__(self, *args, **kwargs):
        print("$$$$$$ UserForm")
        initial = kwargs.get('initial', None)
        instance = kwargs.get('instance', None)

        # Initialize the form
        super(UserForm, self).__init__(*args, **kwargs)
        # self.fields['groups'].label = "Rola"
        # self.fields['groups'].required = True

        # Check if 'initial' is provided or if an 'instance' is provided
        self.fields['phone'].initial = "2137"
        if initial or instance:
            self.fields['email'].disabled = True
            self.fields['group'].initial = instance.groups.first()
            print("INSTANCEEE", self.fields['group'].initial)
        else:
            # Ensure the 'student' field is not disabled
            self.fields['email'].disabled = False


class GroupForm(forms.ModelForm):
    @staticmethod
    def get_name():
        return "Grupa"

    class Meta:
        model = Group
        fields = "__all__"
        exclude = ('id', 'created_by', 'modified_by', 'created_date', 'modified_date')

    name = forms.CharField(label='Nazwa')


class GroupstudentForm(forms.ModelForm):
    @staticmethod
    def get_name():
        return "Członek Grupy"

    class Meta:
        model = GroupStudent
        fields = "__all__"
        exclude = ('id',)


    def update_form(self, data):
        group_id = data.get('group')
        print('updating group')
        if group_id:
            try:
                group = Group.objects.get(pk=group_id)
                self.fields['group'].initial = group
            except Exception:
                pass

    def __init__(self, *args, **kwargs):
        super(GroupstudentForm, self).__init__(*args, **kwargs)
        self.fields['student'].label = 'Uczeń'
        self.fields['group'].disabled = False



def get_form_class(form_name) -> forms:
    """
    Returns the form class based on its name.

    :param form_name: The name of the form class to retrieve.
    :return: The form class.
    """
    try:
        module = importlib.import_module(__name__)
        form_class = getattr(module, form_name)
    except (ImportError, AttributeError):
        raise ValueError(f"Form class '{form_name}' not found.")

    return form_class


class InvoiceForm(forms.ModelForm):
    @staticmethod
    def get_name():
        return "Faktura"

    class Meta:
        model = Invoice
        fields = "__all__"
        exclude = ('id', )

    MONTHS = (
        (1, "Styczeń"),
        (2, "Luty"),
        (3, "Marzec"),
        (4, "Kwiecień"),
        (5, "Maj"),
        (6, "Czerwiec"),
        (7, "Lipiec"),
        (8, "Sierpień"),
        (9, "Wrzesień"),
        (10, "Październik"),
        (11, "Listopad"),
        (12, "Grudzień"),
    )

    month = forms.ChoiceField(label='Miesiąc', choices=MONTHS, initial=MONTHS[dj_timezone.now().month-1][0])
    year = forms.IntegerField(label='Rok', initial=dj_timezone.now().year, min_value=2020)
    am = forms.IntegerField(label='Rok', initial=dj_timezone.now().year, min_value=2020)
    field_order = ['student', 'name', 'month', 'year', 'is_sent']

    def update_form(self, data):
        student_id = data.get('student')
        if student_id:
            try:
                student = Student.objects.get(pk=student_id)
                self.fields['student'].initial = student
            except Exception:
                pass

    def save(self, commit=True):
        instance = super(InvoiceForm, self).save(commit=False)
        instance.invoice_date = datetime.date(int(self.cleaned_data['year']), int(self.cleaned_data['month']), 1)
        if commit:
            instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Nr Faktury'
        self.fields.pop('invoice_date')
        self.fields['is_paid'].label = 'Czy zapłacone?'
        self.fields['is_sent'].label = 'Czy wysłane?'


class InvoiceitemForm(forms.ModelForm):
    @staticmethod
    def get_name():
        return "Pozycja faktury"

    class Meta:
        model = InvoiceItem
        fields = "__all__"
        exclude = ('id', )

    def update_form(self, data):
        invoice_id = data.get('invoice')
        print("invoice_id", invoice_id)
        if invoice_id:
            try:
                invoice = Invoice.objects.get(pk=invoice_id)
                self.fields['invoice'].initial = invoice
            except Exception:
                pass

    def __init__(self, *args, **kwargs):
        super(InvoiceitemForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].label = 'Ilość'
        self.fields['name'].initial = 'Lekcja'
        self.fields['amount'].initial = 120
        self.fields['quantity'].initial = 1
