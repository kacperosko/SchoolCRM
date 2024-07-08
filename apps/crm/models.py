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
# import uuid

#
# class PrefixedUUIDField(models.CharField):
#     PREFIX_MAP = {
#         'Note': '0NT',
#     }
#
#     def __init__(self, prefix_func, *args, **kwargs):
#         self.prefix_func = prefix_func
#         kwargs['max_length'] = len(prefix_func('')) + 36  # Prefix length + UUID length (36 characters)
#         kwargs['unique'] = True
#         super().__init__(*args, **kwargs)
#
#     def pre_save(self, model_instance, add):
#         if add and not getattr(model_instance, self.attname):
#             value = f"{self.prefix}{uuid.uuid4()}"
#             setattr(model_instance, self.attname, value)
#             return value
#         return super().pre_save(model_instance, add)
#
#
# def model_name_prefix(model_name):
#     prefixes = {
#         'Person': '0PR',
#         'Student': '0ST',
#         'StudentPerson': '0SP',
#         'Lesson': '0LS',
#         'LessonAdjustment': '0LA',
#         'Location': '0LC',
#         'Note': '0NT',
#         'WatchRecord': '0WR',
#         'Notification': '0NF',
#
#     }
#     return prefixes.get(model_name, '0EX')


class Note(models.Model):
    content = models.CharField(max_length=200)
    # content = models.TextField()

    # Fields for generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content


class WatchRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, db_index=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.user} is watching {self.content_object}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.message


class Person(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(blank=True, null=True, max_length=16)

    def __str__(self):
        return self.first_name + " " + self.last_name

    def get_full_name(self):
        return self.first_name + " " + self.last_name


class Student(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(blank=True, null=True, max_length=16)
    birthdate = models.DateField(blank=True, null=True)

    notes = GenericRelation(Note)

    # student = models.OneToOneField(Person, on_delete=models.CASCADE, blank=False, null=False,
    #                                related_name='student_student_person_relationship')

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def get_age(self):
        if self.birthdate:
            today = date.today()
            age = today.year - self.birthdate.year - (
                    (today.month, today.day) < (self.birthdate.month, self.birthdate.day)
            )
            return age
        return None

    def __str__(self):
        return self.first_name + " " + self.last_name


class StudentPerson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='student_student_relationship')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='student_person_relationship')
    relationship_type = models.CharField(max_length=100)

    def clean(self):
        if self.student == self.parent:
            raise ValidationError("Student and parent cannot be the same person.")


class Lesson(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_series = models.BooleanField(default=False)
    description = models.CharField(max_length=120, blank=True, null=True)
    series_end_date = models.DateField(blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='lessonSchedule_student_student_relationship')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='lessonSchedule_teacher_user_relationship')


class Statutes:
    PLANNED = 'Zaplanowana'


LESSON_STATUTES = (
    ('Zaplanowana', 'Zaplanowana'),
    ('Nieobecność', 'Nieobecność'),
    ('Odwołana - nauczyciel', 'Odwołana - nauczyciel'),
    ('Odwołana - 24h przed', 'Odwołana - 24h przed')
)


class LessonStatus:
    NIEOBECNOSC = "Nieobecność"
    ODWOLANA_NAUCZYCIEL = "Odwołana - nauczyciel"
    ODWOLANA_24H_PRZED = "Odwołana - 24h przed"


class LessonAdjustment(models.Model):
    original_lesson_date = models.DateTimeField(default=now)
    modified_start_time = models.DateTimeField()
    modified_end_time = models.DateTimeField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='lesson_lesson_relationship')
    status = models.CharField(max_length=64, choices=LESSON_STATUTES, null=True, blank=True)
    comments = models.CharField(max_length=255, blank=True, null=True)


class Absense(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='Absense_teacher_user_relationship')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Location(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)

    notes = GenericRelation(Note)

    def get_full_address(self):
        return self.city + ", ul. " + self.street

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=100)

class GroupStudent(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=False, null=False,)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False,)
