import time
from random import choice, randint
from datetime import timedelta, datetime, date

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from faker import Faker

from apps.crm.models import Student, Location, LessonDefinition, LESSON_STATUTES, Group, GroupStudent, WatchRecord, \
    Note, AttendanceListStudent, AttendanceList, Person, StudentPerson, Event, Invoice, InvoiceItem, AttendanceStatutes
from apps.authentication.models import User
from apps.authentication.models import Group as AuthGroup
from apps.crm.views import watch_record
from django.contrib.contenttypes.models import ContentType
import unicodedata
import re


def ascii_slug(s):
    s = unicodedata.normalize('NFKD', s)
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r'[^a-zA-Z0-9]', '', s)
    return s.lower()

class Command(BaseCommand):
    help = "Generates test data"

    def handle(self, *args, **kwargs):
        fake = Faker('pl_PL')

        LessonDefinition.objects.all().delete()
        Group.objects.all().delete()
        Student.objects.all().delete()
        Person.objects.all().delete()
        Location.objects.all().delete()
        User.objects.all().delete()

        # 0. Generate Users

        from django.core.management import call_command
        call_command('sync_group_permissions')
        users = []
        users_count = 2
        nauczyciele = AuthGroup.objects.get(name='Nauczyciel')
        administratorzy = AuthGroup.objects.get(name='Administrator')
        kierownicy = AuthGroup.objects.get(name='Kierownik')
        for n in range(users_count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"nauczyciel{n+1}@mail.com"
            users.append(User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                phone=fake.phone_number(),
                avatar_color=fake.hex_color()
            ))
        users.append(User(
            email="admin@mail.com",
            first_name="Admin",
            last_name="Testowy",
            is_active=True,
            admin=True,
            is_superuser=True,
            staff=True,
            avatar_color=fake.hex_color()
        ))
        users.append(User(
            email="kierownik@mail.com",
            first_name="Kierownik",
            last_name="Testowy",
            is_active=True,
            admin=True,
            is_superuser=True,
            staff=True,
            user_avatar='avatars/avatar_test.jpg'
        ))
        users_count += 1
        users = User.objects.bulk_create(users)
        for user in users:
            user.set_password('Test123!')
            if user.email == "admin@mail.com":
               administratorzy.user_set.add(user)
            elif user.email == "kierownik@mail.com":
               kierownicy.user_set.add(user)
            else:
                nauczyciele.user_set.add(user)
            user.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully added {users_count} test users'))


        # 1. Generate Students
        students = []
        students_count = 15
        for _ in range(students_count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{ascii_slug(first_name.lower())}@mail.com"
            phone = fake.phone_number()
            birthdate = fake.date_of_birth(minimum_age=20, maximum_age=60)

            students.append(Student(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                birthdate=birthdate,
                created_by=choice(users),
                modified_by=choice(users),
            ))
        students = Student.objects.bulk_create(students)
        self.stdout.write(self.style.SUCCESS(f'Successfully added {students_count} test students'))

        # 2. Get Teachers
        teachers = users

        # 3. Generate Locations (max 3)
        locations = []
        for _ in range(2):
            location = Location.objects.create(
                name="Lokalizacja " + fake.color_name(),
                country="Polska",
                city="Wrocław",
                street=fake.street_name(),
                postal_code=fake.postcode()
            )
            locations.append(location)
        self.stdout.write(self.style.SUCCESS('Successfully added 3 locations'))

        # 4. Generate Groups and associate Students
        groups = []
        for group_name in ["Grupa A", "Grupa B"]:
            group = Group.objects.create(name=group_name, created_by=choice(users), modified_by=choice(users))
            groups.append(group)

        # Losowo przypisz uczniów do grup
        for student in students[:len(students)//2]:
            assigned_group = choice(groups)
            GroupStudent.objects.create(group=assigned_group, student=student)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(groups)} groups and assigned students'))

        # 5. Generate Lessons for Groups
        # --- Predefiniowane daty i godziny (15 sztuk) ---
        predefined_lessons = [
            datetime(2025, 8, 4, 9, 0),
            datetime(2025, 8, 4, 10, 0),
            datetime(2025, 8, 4, 13, 0),
            datetime(2025, 8, 5, 10, 0),
            datetime(2025, 8, 5, 12, 0),
            datetime(2025, 8, 5, 15, 0),
            datetime(2025, 8, 6, 12, 0),
            datetime(2025, 8, 6, 13, 0),
            datetime(2025, 8, 6, 14, 0),
            datetime(2025, 8, 7, 13, 0),
            datetime(2025, 8, 7, 14, 0),
            datetime(2025, 8, 7, 16, 0),
            datetime(2025, 8, 8, 9, 0),
            datetime(2025, 8, 8, 11, 0),
            datetime(2025, 8, 8, 14, 0),
        ]

        students = list(Student.objects.all())
        locations = list(Location.objects.all())
        groups = list(Group.objects.all())

        created_lessons = []

        for idx, start_dt in enumerate(predefined_lessons):
            student = choice(students)
            teacher = choice(teachers)
            location = choice(locations)

            # każdej grupie dajemy dokładnie jedną lekcję powtarzającą
            group = None
            if idx < len(groups):
                group = groups[idx]

            lesson = LessonDefinition.objects.create(
                start_time=start_dt.time(),
                lesson_date=start_dt.date(),
                duration=60,
                is_series=True,
                description=f"Lekcja testowa {idx + 1}",
                student=student if group is None else None,
                teacher=teacher,
                location=location,
                group=group if group else None
            )
            created_lessons.append(lesson)

        print(f"Utworzono {len(created_lessons)} lekcji")

        # Tworzenie listy obecności
        today = datetime.now().date()

        events = Event.objects.filter(event_date__lte=today, lesson_definition__group__isnull=False)
        # group_students = {}
        # for group in groups:
        #     group_students[group.id] = GroupStudent.objects.filter(group_id=group.id)

        # list_student = []
        for event in events:
            AttendanceList.objects.create(group_id=event.lesson_definition.group.id,
                                                            event_id=event.id, created_by=choice(teachers),
                                                            modified_by=choice(teachers))
        print(f"Utworzono listy obecności dla {events.count()} eventów")

        attendances = AttendanceListStudent.objects.all()
        for attendance in attendances:
            attendance.attendance_status = choice(AttendanceStatutes.values)
            attendance.save()

        #7 Tworzenie watch records i kilka notatek
        watch_records = []
        content_type_location = ContentType.objects.get(model='location', app_label='crm')
        content_type_student = ContentType.objects.get(model='student', app_label='crm')
        content_type_group = ContentType.objects.get(model='group', app_label='crm')
        for teacher in teachers:
            for location in locations:
                watch_records.append(WatchRecord(
                    user=teacher,
                    content_type=content_type_location,
                    object_id=location.id
                ))
            for student in students:
                watch_records.append(WatchRecord(
                    user=teacher,
                    content_type=content_type_student,
                    object_id=student.id
                ))
            for group in groups:
                watch_records.append(WatchRecord(
                    user=teacher,
                    content_type=content_type_group,
                    object_id=group.id
                ))
        WatchRecord.objects.bulk_create(watch_records)

        for _ in range(5):
            student = choice(Student.objects.all())
            Note.objects.create(
                content = fake.text(max_nb_chars=128),
                content_type = content_type_student,
                object_id = student.id,
                created_by = choice(teachers),
            )
        for location in locations:
            Note.objects.create(
                content = fake.text(max_nb_chars=128),
                content_type = content_type_location,
                object_id = location.id,
                created_by = choice(teachers),
            )
        for group in groups:
            Note.objects.create(
                content=fake.text(max_nb_chars=128),
                content_type=content_type_group,
                object_id=group.id,
                created_by=choice(teachers),
            )

        print(f"Utworzono notatki")

        relations = ['Matka', 'Ojciec', 'Babcia', 'Dziadek', 'Inna']

        # tworzenie kontaktów
        for _ in range(20):
            student = choice(students)
            person = Person.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number(),
            )
            StudentPerson.objects.create(
                person=person,
                student=student,
                relationship_type=choice(relations)
            )

        #9 Tworzenie faktur

        instruments = ["Skrzypce", "Saksofon", "Śpiew", "Pianino"]
        students = Student.objects.all()

        created_invoices = []

        for student in students:
            invoice = Invoice.objects.create(
                name=f"Faktura sierpień 2025 - {student.first_name} {student.last_name}",
                student=student,
                invoice_date=date(2025, 8, 1),
                is_paid=choice([True, False]),
                is_sent=choice([True, False])
            )

            InvoiceItem.objects.create(
                invoice=invoice,
                name=f"Lekcja {choice(instruments)}",
                quantity=randint(3, 6),
                amount=randint(80, 140),
            )

            created_invoices.append(invoice)

        print(f"Utworzono {len(created_invoices)} faktur dla sierpnia")
