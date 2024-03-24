from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from rest_framework import serializers


# Create your models here.

class Person(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.first_name + " " + self.last_name

    def get_full_name(self):
        return self.first_name + " " + self.last_name


class Student(models.Model):
    student = models.OneToOneField(Person, on_delete=models.CASCADE, blank=False, null=False,
                                   related_name='student_student_person_relationship')
    parent = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True,
                               related_name='student_parent_person_relationship')

    def __str__(self):
        return self.student.first_name + " " + self.student.last_name

    def clean(self):
        if self.student == self.parent:
            raise ValidationError("Student and parent cannot be the same person.")


WEEK_DAYS = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
)


class Lesson(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_series = models.BooleanField(default=False)
    series_end_date = models.DateField(blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='lessonSchedule_student_student_relationship')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='lessonSchedule_teacher_user_relationship')


LESSON_STATUTES = (
    ('Planned', 'Planned'),
    ('Canceled', 'Canceled')
)


class LessonAdjustment(models.Model):
    original_lesson_date = models.DateTimeField(default=now)
    modified_start_time = models.DateTimeField()
    modified_end_time = models.DateTimeField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='lesson_lesson_relationship')
    status = models.CharField(max_length=64, choices=LESSON_STATUTES, null=True, blank=True)
    comments = models.CharField(max_length=255, blank=True, null=True)

# class LessonScheduleSerializer(serializers.ModelSerializer):
#     student_obj = serializers.SerializerMethodField()
#
#     def get_student_obj(self, obj):
#         return {'id': obj.student.student.id, 'name': obj.student.student.firstName + " " + obj.student.student.lastName}
#
#     class Meta:
#         model = LessonSchedule
#         fields = '__all__'
# class LessonException(models.Model):
#     date = models.DateTimeField()
#     student = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True,
#                                 related_name='lessonException_student_student_relationship')
#     teacher = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
#                                 related_name='lessonException_teacher_user_relationship')
