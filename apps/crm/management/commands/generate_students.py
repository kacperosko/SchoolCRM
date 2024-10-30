from django.core.management.base import BaseCommand
from faker import Faker
from apps.crm.models import Student  # Zaimportuj model Student


class Command(BaseCommand):
    help = "Generates test students"

    def handle(self, *args, **kwargs):
        fake = Faker('pl_PL')  # Polski język dla losowych danych
        students = []

        for _ in range(100):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            phone = fake.phone_number()
            birthdate = fake.date_of_birth(minimum_age=20, maximum_age=60)

            # Tworzymy instancję studenta
            students.append(Student(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                birthdate=birthdate
            ))

        # Dodajemy wszystkie rekordy naraz
        Student.objects.bulk_create(students)
        self.stdout.write(self.style.SUCCESS('Successfully added 100 test students'))
