from random import choice, randint
from datetime import timedelta, datetime

from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from faker import Faker

from apps.crm.models import Student, Location, Lesson, LessonAdjustment, LESSON_STATUTES
from apps.authentication.models import User


class Command(BaseCommand):
    help = "Generates test data"

    def handle(self, *args, **kwargs):
        fake = Faker('pl_PL')

        # 1. Generate Students
        students = []
        for _ in range(20):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            phone = fake.phone_number()
            birthdate = fake.date_of_birth(minimum_age=20, maximum_age=60)

            students.append(Student(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                birthdate=birthdate
            ))
        students = Student.objects.bulk_create(students)
        self.stdout.write(self.style.SUCCESS('Successfully added 20 test students'))

        # 2. Get Teachers
        teachers = User.objects.all()

        # 3. Generate Locations (max 3)
        locations = []
        for _ in range(3):
            location = Location.objects.create(
                name=fake.company(),
                country=fake.country(),
                city=fake.city(),
                street=fake.street_address(),
                postal_code=fake.postcode()
            )
            locations.append(location)
        self.stdout.write(self.style.SUCCESS('Successfully added 3 locations'))

        # 4. Generate Lessons and Lesson Adjustments
        start_date = datetime(2024, 10, 1)
        end_date = datetime(2024, 10, 31)
        lesson_time_range = range(8, 18)  # Lessons between 8:00 and 18:00

        lesson_series = []  # Store recurring lessons to add adjustments later

        for single_date in (start_date + timedelta(days=n) for n in range((end_date - start_date).days + 1)):
            start_hour = choice(lesson_time_range)
            start_time = make_aware(datetime.combine(single_date, datetime.min.time().replace(hour=start_hour)))
            end_time = start_time + timedelta(hours=1)
            is_series = bool(randint(0, 1))  # 50% chance to be a series

            # Randomly select a student, teacher, and location
            student = choice(students)
            teacher = choice(teachers)
            location = choice(locations)

            lesson = Lesson.objects.create(
                start_time=start_time,
                end_time=end_time,
                is_series=is_series,
                description=fake.text(max_nb_chars=120),
                series_end_date=single_date + timedelta(weeks=4) if is_series else None,
                student=student,
                teacher=teacher,
                location=location
            )

            if is_series:
                lesson_series.append(lesson)

        self.stdout.write(self.style.SUCCESS('Successfully added lessons with some as series'))

        # 5. Create Lesson Adjustments for series
        for lesson in lesson_series:
            # Create a random date within the series for an adjustment
            lesson_date = lesson.start_time.date()
            adjustment_date = lesson_date + timedelta(weeks=1)  # Adjust on the next occurrence in the series

            # Make sure the adjustment date is within the series range
            if lesson.series_end_date and adjustment_date <= lesson.series_end_date:
                modified_start_time = lesson.start_time + timedelta(weeks=1)
                modified_end_time = lesson.end_time + timedelta(weeks=1)

                LessonAdjustment.objects.create(
                    original_lesson_date=lesson.start_time,
                    modified_start_time=modified_start_time,
                    modified_end_time=modified_end_time,
                    lesson=lesson,
                    status=choice(LESSON_STATUTES)[0],
                    comments=fake.sentence(),
                    teacher=lesson.teacher,
                    location=lesson.location
                )

        self.stdout.write(self.style.SUCCESS('Successfully added lesson adjustments for series lessons'))
