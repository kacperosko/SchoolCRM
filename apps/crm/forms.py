from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.test import override_settings
from django.core.exceptions import ValidationError

from .models import Location, Person, Student, Lesson, StudentPerson, GroupStudent, Group, AttendanceList, Invoice
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
        return "Student"

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


class LessonForm(forms.ModelForm):
    @staticmethod
    def get_name():
        return "Lekcja"

    @staticmethod
    def get_help_text():
        return "Je\u015Bli chcesz edytowa\u0107 dat\u0119 lekcji w serii musisz ustawi\u0107 dat\u0119 zako\u0144czenia obecnej serii i utworzy\u0107 now\u0105 seri\u0119 z inn\u0105 dat\u0105. Ostatnia lekcja odbędzie się w datę zakończenia serii lub przed nią jeśli dotyczy innego dnia tygodnia."

    class Meta:
        model = Lesson
        fields = "__all__"
        exclude = ('id',)

    start_time = forms.DateTimeField(label='Data rozpocz\u0119cia', disabled=True,
                                     widget=forms.DateInput(attrs={'type': 'datetime-local', 'class': 'mt--2'}))
    end_time = forms.DateTimeField(label='Data zako\u0144czenia', disabled=True,
                                   widget=forms.DateInput(attrs={'type': 'datetime-local', 'class': 'mt--2'}))
    is_series = forms.BooleanField(label='Powtarzanie co tydzie\u0144', disabled=True, required=False)
    description = forms.CharField(label='Opis')
    series_end_date = forms.DateTimeField(label='Data zako\u0144czenia serii', required=False,
                                          widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt--2'}))

    def clean(self):
        cleaned_data = super().clean()
        end_time = cleaned_data.get("end_time")
        series_end_date = cleaned_data.get("series_end_date")

        validation_errors = {}


        if series_end_date and end_time and series_end_date < end_time:
            validation_errors['series_end_date'] = "Data zako\u0144czenia serii nie mo\u017Ce by\u0107 wcze\u015Bniejsza ni\u017C data zako\u0144czenia"

        if len(validation_errors) > 0:
            raise ValidationError(validation_errors)

        return cleaned_data

    def __init__(self, *args, **kwargs):
        # user = kwargs.pop('user','')
        super(LessonForm, self).__init__(*args, **kwargs)
        self.fields['student'].label = 'Student'
        if self.fields['student'].initial:
            self.fields['student'].disabled = True
        else:
            self.fields['group'].disabled = True
        self.fields['teacher'].label = 'Nauczyciel'
        self.fields['location'].label = 'Lokalizacja'


class UserForm(forms.ModelForm):

    @staticmethod
    def get_name():
        return "Nauczyciel"

    class Meta:
        model = User
        fields = "__all__"
        exclude = ('id', 'password', 'is_active', 'is_staff', 'is_superuser', 'staff', 'admin', 'user_permissions', 'last_login', 'user_avatar')

    email = forms.CharField(label='Email', disabled=True)
    first_name = forms.CharField(label='Imi\u0119')
    last_name = forms.CharField(label='Nazwisko')
    phone = forms.CharField(label='Telefon', max_length=20, required=False)
    avatar_color = forms.CharField(label='Kolor awatara', widget=forms.TextInput(attrs={'type': 'color'}))

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', None)
        instance = kwargs.get('instance', None)

        # Initialize the form
        super(UserForm, self).__init__(*args, **kwargs)

        # Check if 'initial' is provided or if an 'instance' is provided
        if initial or instance:
            # Disable the 'student' field
            self.fields['email'].disabled = True
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
        self.fields['student'].label = 'Student'
        self.fields['group'].disabled = False



class AttendancelistForm(forms.ModelForm):
    @staticmethod
    def get_name():
        return "Lista Obecności"

    class Meta:
        model = AttendanceList
        fields = "__all__"
        exclude = ('id', 'created_by', 'modified_by', 'created_date', 'modified_date')

    lesson_date = forms.DateTimeField(label='Data lekcji', disabled=False,
                                     widget=forms.DateInput(attrs={'type': 'datetime-local', 'class': 'mt--2'}))
 
    def update_form(self, data):
        group_id = data.get('group')
        print('updating group')
        if group_id:
            try:
                group = Group.objects.get(pk=group_id)
                self.fields['group'].initial = group
                self.fields['group'].disabled = True
            except Exception:
                pass

    def __init__(self, *args, **kwargs):
        super(AttendancelistForm, self).__init__(*args, **kwargs)
        # self.fields['lesson_date'].label = 'Data Lekcji'
        self.fields['group'].disabled = True


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
