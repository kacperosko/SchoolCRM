from smtplib import SMTPException

from django.db import models

from apps.authentication.models import User
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from SchoolCRM.settings import EMAIL_HOST_USER, SITE_URL
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from datetime import date
import uuid

import uuid


class PrefixedUUIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 39)  # 3 (prefix) + 29 (UUID) = 32
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        self.model = cls
        self.prefix = model_name_prefix(cls.__name__)

    def pre_save(self, model_instance, add):
        if add and not getattr(model_instance, self.attname):
            value = f"{self.prefix}{uuid.uuid4()}"
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)


def model_name_prefix(model_name):
    prefixes = {
        'Person': '0PR',
        'Student': '0ST',
        'StudentPerson': '0SP',
        'Lesson': '0LS',
        'LessonAdjustment': '0LA',
        'Location': '0LC',
        'Note': '0NT',
        'WatchRecord': '0WR',
        'Notification': '0NF',
    }
    return prefixes.get(model_name, '0EX')


def get_model_by_prefix(prefix):
    prefixes = {
        '0PR': 'Person',
        '0ST': 'Student',
        '0SP': 'StudentPerson',
        '0LS': 'Lesson',
        '0LA': 'LessonAdjustment',
        '0LC': 'Location',
        '0NT': 'Note',
        '0WR': 'WatchRecord',
        '0NF': 'Notification',
    }
    return prefixes.get(prefix, None)


class Note(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    content = models.CharField(max_length=200)

    # Fields for generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=32, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_model_name(self, language):
        names = {
            "pl": "Notatka"
        }
        return names.get(language, self.__class__.__name__)

    def __str__(self):
        return self.content


class WatchRecord(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, db_index=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=32, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.user} is watching {self.content_object}"


class Notification(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=32, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def get_model_name(self, language):
        names = {
            "pl": "Powiadomienie"
        }
        return names.get(language, self.__class__.__name__)

    def __str__(self):
        return self.message


class Person(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(blank=True, null=True, max_length=16)

    def get_model_name(self, language):
        names = {
            "pl": "Kontakt"
        }
        return names.get(language, self.__class__.__name__)

    def __str__(self):
        return self.first_name + " " + self.last_name

    def get_full_name(self):
        return self.first_name + " " + self.last_name


class Student(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(blank=True, null=True, max_length=16)
    birthdate = models.DateField(blank=True, null=True)

    notes = GenericRelation(Note)

    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='Student_created_by')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='Student_modified_by')
    modified_date = models.DateTimeField(auto_now=True)

    def get_model_name(self, language):
        names = {
            "pl": "Student"
        }
        return names.get(language, self.__class__.__name__)

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def get_age(self):
        if self.birthdate:
            today = date.today()
            age = today.year - self.birthdate.year - (
                    (today.month, today.day) < (self.birthdate.month, self.birthdate.day))
            return age
        return None

    def __str__(self):
        return self.first_name + " " + self.last_name


class StudentPerson(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='student_student_relationship')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='student_person_relationship')
    relationship_type = models.CharField(max_length=100)

    def clean(self):
        if self.student == self.person:
            raise ValidationError("Student and parent cannot be the same person.")


class Location(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)

    notes = GenericRelation(Note)

    def get_full_name(self):
        return self.city + ", ul. " + self.street

    def get_model_name(self, language):
        names = {
            "pl": "Lokalizacja"
        }
        return names.get(language, self.__class__.__name__)

    def __str__(self):
        return self.name + ", adres: " + self.country + ", city: " + self.city + ", street: " + self.street + ", postal code: " + self.postal_code


class Lesson(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_series = models.BooleanField(default=False)
    description = models.CharField(max_length=120, blank=True, null=True)
    series_end_date = models.DateField(blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='lessonSchedule_student_student_relationship')
    teacher = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=False, null=False,
                                related_name='lessonSchedule_teacher_user_relationship')
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, blank=False, null=False,
                                 related_name='lessonSchedule_location_relationship')

    def get_model_name(self, language):
        names = {
            "pl": "Lekcja"
        }
        return names.get(language, self.__class__.__name__)


class Statutes:
    PLANNED = 'Zaplanowana'
    NIEOBECNOSC = "Nieobecnosc"
    ODWOLANA_NAUCZYCIEL = "Odwolana - nauczyciel"
    ODWOLANA_24H_PRZED = "Odwolana - 24h przed"


LESSON_STATUTES = (
    ('Zaplanowana', 'Zaplanowana'),
    ('Nieobecnosc', 'Nieobecność'),
    ('Odwolana - nauczyciel', 'Odwołana - nauczyciel'),
    ('Odwolana - 24h przed', 'Odwołana - 24h przed')
)


class LessonAdjustment(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    original_lesson_date = models.DateTimeField(default=now)
    modified_start_time = models.DateTimeField()
    modified_end_time = models.DateTimeField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='lesson_lesson_relationship')
    status = models.CharField(max_length=64, choices=LESSON_STATUTES, null=True, blank=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    teacher = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=False, null=False,
                                related_name='lessonAdjustment_teacher_user_relationship')
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, blank=False, null=False,
                                 related_name='lessonAdjustment_location_relationship')


class Absense(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='Absense_teacher_user_relationship')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Group(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    name = models.CharField(max_length=100)


class GroupStudent(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=False, null=False, )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False, )


def get_model_object_by_prefix(prefix):
    prefixes = {
        '0PR': Person,
        '0ST': Student,
        '0SP': StudentPerson,
        '0LS': Lesson,
        '0LA': LessonAdjustment,
        '0LC': Location,
        '0NT': Note,
        '0WR': WatchRecord,
        '0NF': Notification,
    }
    return prefixes.get(prefix, None)
