from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from rest_framework import serializers


# Create your models here.

class Person(models.Model):
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.IntegerField(blank=True, null=True)
    birthdate = models.DateField()

    def __str__(self):
        return self.firstName + " " + self.lastName

    def get_full_name(self):
        return self.firstName + " " + self.lastName


class Student(models.Model):
    student = models.OneToOneField(Person, on_delete=models.CASCADE, blank=False, null=False,
                                   related_name='student_student_person_relationship')
    parent = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True,
                               related_name='student_parent_person_relationship')

    def __str__(self):
        return self.student.firstName + " " + self.student.lastName

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


class LessonSchedule(models.Model):
    weekDay = models.CharField(choices=WEEK_DAYS, max_length=10)
    startTime = models.TimeField()
    endTime = models.TimeField()
    startDate = models.DateField(default=now)
    endDate = models.DateField(blank=True, null=True)

    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='lessonSchedule_student_student_relationship')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='lessonSchedule_teacher_user_relationship')


LESSON_STATUTES = (
    ('Completed', 'Completed'),
    ('Canceled', 'Canceled')
)


class LessonAdjustment(models.Model):
    lessonDate = models.DateField()
    originalLessonDate = models.DateField(default=now)
    startTime = models.TimeField()
    endTime = models.TimeField()
    lessonSchedule = models.ForeignKey(LessonSchedule, on_delete=models.CASCADE, blank=False, null=False,
                                       related_name='lessonSchedule_lessonSchedule_relationship')
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
