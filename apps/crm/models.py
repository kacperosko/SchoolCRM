from django.db import models

from apps.authentication.models import User
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from datetime import date

from ..service_helper import PrefixedUUIDField


class Note(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    content = models.CharField(max_length=200)

    # Fields for generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=39, null=True, blank=True)
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
    object_id = models.CharField(max_length=39, null=True, blank=True)
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
    object_id = models.CharField(max_length=39, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def get_model_name(self, language):
        names = {
            "pl": "Powiadomienie"
        }
        return names.get(language, self.__class__.__name__)

    def __str__(self):
        return self.message


class FieldHistory(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=39)
    content_object = GenericForeignKey('content_type', 'object_id')

    field_name = models.CharField(max_length=255)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)

    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.content_object} - {self.field_name} changed"


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

    class Meta:
        verbose_name = "Kontakt"
        verbose_name_plural = "Kontakty"


class Student(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(blank=True, null=True, max_length=16)
    birthdate = models.DateField(blank=True, null=True)

    notes = GenericRelation(Note)
    history = GenericRelation(FieldHistory)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='Student_created_by', null=True,
                                   blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='Student_modified_by', null=True,
                                    blank=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Studenci'
        verbose_name = 'Student'

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


RELATIONSHIPS = (
    ('Matka', 'Matka'),
    ('Ojciec', 'Ojciec'),
    ('Babcia', 'Babcia'),
    ('Dziadek', 'Dziadek'),
    ('Inna', 'Inna'),
)


class StudentPerson(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='student_student_relationship')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='student_person_relationship')
    relationship_type = models.CharField(max_length=100, choices=RELATIONSHIPS)

    def __str__(self):
        return f"Relacja '{self.relationship_type}' {self.person} ze studentem {self.student}"

    def get_model_name(self, language):
        names = {
            "pl": "Relacja ze Studentem"
        }
        return names.get(language, self.__class__.__name__)

    def redirect_after_edit(self):
        return f'/student/{self.student.id}'

    def redirect_after_delete(self):
        return f'/student/{self.student.id}'


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
        return self.name + ", " + self.country + " " + self.city + " " + self.postal_code + ", ul. " + self.street

    class Meta:
        verbose_name = "Lokalizacja"
        verbose_name_plural = "Lokalizacje"


class Group(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    name = models.CharField(max_length=32)
    notes = GenericRelation(Note)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='group_created_by', null=True,
                                   blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='group_modified_by', null=True,
                                    blank=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_full_name(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Grupy'
        verbose_name = 'Grupa'


class LessonStatutes(models.TextChoices):
    ZAPLANOWANA = 'zaplanowana', 'Zaplanowana'
    NIEOBECNOSC = 'nieobecnosc', 'Nieobecność'
    ODWOLANA_NAUCZYCIEL = 'odwolana_nauczyciel', 'Odwołana - nauczyciel'
    ODWOLANA_24H_PRZED = 'odwolana_24h_przed', 'Odwołana - 24h przed'


# TODO change values without spaces
LESSON_STATUTES = (
    ('Zaplanowana', 'Zaplanowana'),
    ('Nieobecnosc', 'Nieobecno\u015B\u0107'),
    ('Odwolana - nauczyciel', 'Odwo\u0142ana - nauczyciel'),
    ('Odwolana - 24h przed', 'Odwo\u0142ana - 24h przed')
)


class LessonDuration(models.IntegerChoices):
    SHORT = 30, '30 min'
    MEDIUM = 45, '45 min'
    NORMAL = 60, '60 min'


class LessonDefinition(models.Model):
    id = PrefixedUUIDField(primary_key=True)
    lesson_date = models.DateField()
    start_time = models.TimeField()
    duration = models.IntegerField(choices=LessonDuration.choices, blank=False, null=False, )
    description = models.CharField(max_length=255, null=True, blank=True)

    # series fields
    series_end_date = models.DateField(blank=True, null=True)
    is_series = models.BooleanField(default=False)

    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True, )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True, )

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, )
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=False, null=False, )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_student_or_group",
                check=(
                        models.Q(student__isnull=True, group__isnull=False) | models.Q(student__isnull=False, group__isnull=True)
                ),
            )
        ]


class EventType(models.TextChoices):
    LESSON = 'lesson', 'Lekcja'
    STANDARD = 'standard', 'Standardowe Wydarzenie'


week_days_pl = {
        0: "Poniedzia\u0142ek",
        1: "Wtorek",
        2: "\u015Aroda",
        3: "Czwartek",
        4: "Pi\u0105tek",
        5: "Sobota",
        6: "Niedziela"
    }


class Event(models.Model):
    # Type
    event_type = models.CharField(max_length=32, choices=EventType.choices, default=EventType.STANDARD)

    # Standard fields
    id = PrefixedUUIDField(primary_key=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    event_date = models.DateField()
    description = models.CharField(max_length=255,  blank=True, null=True)

    # Lesson Fields
    lesson_definition = models.ForeignKey(LessonDefinition, on_delete=models.CASCADE, blank=False, null=False, )
    status = models.CharField(max_length=100, choices=LessonStatutes.choices, blank=False, null=False, )
    original_lesson_datetime = models.DateTimeField()
    duration = models.IntegerField(choices=LessonDuration.choices, blank=False, null=False, )
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False, )
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=False, null=False, )

    def to_dict(self):
        return {
            'start_date': self.event_date,
            'start_time': self.start_time.strftime("%H:%M"),
            'end_time': self.end_time.strftime("%H:%M"),
            'lesson_id': self.id,
            'status': self.status,
            'status_label': self.get_status_display(),
            'weekday': week_days_pl[self.event_date.weekday()],
            'description': self.description if self.description else self.lesson_definition.description if self.lesson_definition else '',
            'teacher': self.teacher.get_full_name(),
            'teacher_id': self.teacher.id,
            'location': str(self.location),
            'location_id': self.location.id,
            'duration': self.duration,
            'original_date': self.original_lesson_datetime.date() if self.original_lesson_datetime else None,
            'original_time': self.original_lesson_datetime.time().strftime("%H:%M") if self.original_lesson_datetime else None,
            'is_series': self.lesson_definition.is_series if self.lesson_definition else False,
        }


class Lesson(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_series = models.BooleanField(default=False)
    description = models.CharField(max_length=120, blank=True, null=True)
    series_end_date = models.DateField(blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True,
                                related_name='lessonSchedule_student_student_relationship')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True,
                              related_name='lessonSchedule_lesson_group_relationship')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, blank=False, null=True,
                                related_name='lessonSchedule_teacher_user_relationship')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=False, null=True,
                                 related_name='lessonSchedule_location_relationship')

    def clean(self):
        # Ensure either student or group is set, but not both
        if self.student and self.group:
            raise ValidationError('You can only assign a lesson to either a student or a group, not both.')
        if not self.student and not self.group:
            raise ValidationError('A lesson must be assigned to either a student or a group.')

    def save(self, *args, **kwargs):
        # Call clean before saving to ensure validation is applied
        self.clean()
        super().save(*args, **kwargs)

    def get_model_name(self, language):
        names = {
            "pl": "Lekcja"
        }
        return names.get(language, self.__class__.__name__)

    def __str__(self):
        return self.description + " " + str(self.start_time.time())[:5] + " - " + str(self.end_time.time())[
                                                                                  :5] + " " + self.location.get_full_name()

    def redirect_after_delete(self):
        if self.student is None:
            return f'/group/{self.group.id}/lesson-series'
        return f'/student/{self.student.id}/lesson-series'

    def redirect_after_edit(self):
        if self.student is None:
            return f'/group/{self.group.id}/lesson-series'
        return f'/student/{self.student.id}/lesson-series'


class LessonAdjustment(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    original_lesson_date = models.DateTimeField(default=now)
    modified_start_time = models.DateTimeField()
    modified_end_time = models.DateTimeField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='lesson_lesson_relationship')
    status = models.CharField(max_length=64, choices=LESSON_STATUTES, null=True, blank=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, blank=False, null=True,
                                related_name='lessonAdjustment_teacher_user_relationship')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=False, null=True,
                                 related_name='lessonAdjustment_location_relationship')


class Absense(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='Absense_teacher_user_relationship')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class GroupStudent(models.Model):
    id = PrefixedUUIDField(primary_key=True)

    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=False, null=False,
                              related_name='group_student_group_relationship')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='groupStudent_student_relationship')

    class Meta:
        unique_together = ('group', 'student')

    def __str__(self):
        return f"Student {self.student.get_full_name()} w grupie {self.group.get_full_name()}"

    def redirect_after_delete(self):
        return f'/group/{self.group.id}'

    def redirect_after_edit(self):
        return f'/group/{self.group.id}'


class AttendanceList(models.Model):
    id = PrefixedUUIDField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=False, null=False,
                              related_name='attendance_group_relationship')
    lesson_date = models.DateTimeField()

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='attenndancelist_createdby', null=True,
                                   blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='attenndancelist_modified_by',
                                    null=True,
                                    blank=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lista Obecności {self.lesson_date.strftime('%d-%m-%y %H:%M')}"

    def redirect_after_edit(self):
        return f'/attendancelist/{self.id}'

    def redirect_after_delete(self):
        return f'/group/{self.group.id}?tab=Attendance'


class AttendanceStatutes:
    OBECNOSC = "Obecnosc"
    NIEOBECNOSC = "Nieobecnosc"
    SPOZNIENIE = "Spoznienie"


ATTENDANCE_STATUTES = (
    ('Obecnosc', 'Obecno\u015B\u0107'),
    ('Nieobecnosc', 'Nieobecno\u015B\u0107'),
    ('Spoznienie', 'Spóźnienie'),
)


class AttendanceListStudent(models.Model):
    id = PrefixedUUIDField(primary_key=True)
    attendance_list = models.ForeignKey(AttendanceList, on_delete=models.CASCADE, blank=False, null=False,
                                        related_name='attendance_list_student_group_relationship')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False, )
    attendance_status = models.CharField(max_length=64, choices=ATTENDANCE_STATUTES, null=True, blank=True,
                                         default="Obecnosc")


class Invoice(models.Model):
    id = PrefixedUUIDField(primary_key=True)
    name = models.CharField(max_length=64, blank=False, null=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=False, null=False, )
    invoice_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.name + " " + self.invoice_date.strftime("%d-%m-%y")

    def get_total_amount(self):
        total = sum(item.amount * item.quantity for item in self.invoiceitem_set.all())
        return total

    def redirect_after_edit(self):
        return f'/student/{self.student.id}?tab=Invoices'

    def redirect_after_delete(self):
        return f'/student/{self.student.id}?tab=Invoices'

    def get_model_name(self, language):
        names = {
            "pl": "Faktura"
        }
        return names.get(language, self.__class__.__name__)


class InvoiceItem(models.Model):
    id = PrefixedUUIDField(primary_key=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, blank=False, null=False, )
    name = models.CharField(max_length=255)
    amount = models.IntegerField()
    quantity = models.IntegerField()


