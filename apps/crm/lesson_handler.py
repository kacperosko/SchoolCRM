from datetime import datetime, timedelta, date, time
from .models import Student, Lesson, LessonAdjustment, Person, Statutes
from django.utils import timezone as dj_timezone
from collections import defaultdict
from django.db.models import Q


class LessonHandler:
    week_days_pl = {
        0: "Poniedzia\u0142ek",
        1: "Wtorek",
        2: "\u015Aroda",
        3: "Czwartek",
        4: "Pi\u0105tek",
        5: "Sobota",
        6: "Niedziela"
    }

    def __init__(self, start_date: date, end_date: date, start_time: time, end_time: time, lesson_id,
                 description, teacher, student, location, original_date=None, status=Statutes.PLANNED, is_adjustment=False):
        self.start_date = start_date.strftime('%d-%m-%Y')
        self.end_date = end_date.strftime('%d-%m-%Y')
        self.start_time = start_time.strftime('%H:%M')
        self.end_time = end_time.strftime('%H:%M')
        self.lesson_id = lesson_id
        self.status = status
        self.weekday = self.week_days_pl[start_date.weekday()]
        self.is_adjustment = is_adjustment
        self.description = description
        self.teacher = teacher
        self.student = student.get_full_name() if student else None
        self.student_id = student.id if student else None
        self.location = location
        time_difference = end_time - start_time
        self.duration = time_difference.total_seconds() / 60
        if original_date:
            self.original_date = original_date.date().strftime('%d-%m-%Y')
            self.original_time = original_date.time().strftime('%H:%M')
        else:
            self.original_date = None
            self.original_time = None

    def to_dict(self):
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'lesson_id': self.lesson_id,
            'status': self.status,
            'weekday': self.weekday,
            'is_adjustment': self.is_adjustment,
            'description': self.description if self.description else '',
            'teacher': self.teacher,
            'location': self.location,
            'duration': self.duration,
            'original_date': self.original_date if self.original_date else None,
            'original_time': self.original_time if self.original_time else None,
        }

    def __str__(self):
        return f"start_date: {self.start_date}, end_date: {self.end_date}, start_time: {self.start_time}, end_time: {self.end_time}, original_date: {self.original_date}, status: {self.status}"


def generate_lesson_dict_key(start_time: datetime, lesson_id):
    return start_time.strftime("%d_%m_%Y-%H:%M") + "_" + str(lesson_id)


def count_lessons_for_student_in_year(student_id, year):
    lessons = Lesson.objects.filter(
        Q(student_id=student_id) &
        Q(start_time__year__lte=year) &
        (
            (Q(series_end_date__year__gte=year) |
             Q(series_end_date=None))
        )
    )

    adjustments = LessonAdjustment.objects.filter(
        Q(lesson__student_id=student_id) &
        (
                Q(original_lesson_date__year=year) |
                Q(modified_start_time__year=year)
        )
    )

    return generate_lessons(lessons, adjustments, year)


def count_lessons_for_student_in_month(student_id, year, month):
    first_day_of_month = date(year, month, 1)
    if month == 12:
        last_day_of_month = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day_of_month = date(year, month + 1, 1) - timedelta(days=1)
    lessons = Lesson.objects.filter(
        Q(student_id=student_id) &
        (
            # 1. Lekcje jednorazowe (nie są serią) i zaczynają się w wybranym miesiącu
            Q(is_series=False) &
            Q(start_time__year=year) &
            Q(start_time__month=month)
        ) |
        (
            # 2. Lekcje będące serią, które zaczynają się przed końcem wybranego miesiąca
            Q(student_id=student_id) &
            Q(is_series=True) &
            Q(start_time__lte=last_day_of_month) &  # Seria musi zacząć się przed końcem miesiąca
            (
                # a) Seria nie ma daty zakończenia
                Q(series_end_date__isnull=True) |
                # b) Seria kończy się po ostatnim dniu miesiąca
                Q(series_end_date__gte=last_day_of_month)
            )
        )
    )

    adjustments = LessonAdjustment.objects.filter(
        Q(lesson__student_id=student_id) &
        (
            (
                Q(original_lesson_date__year=year) &
                Q(original_lesson_date__month=month)
            ) |
            (
                Q(modified_start_time__year=year) &
                Q(modified_start_time__month=month)
            )
        )
    )
    if not adjustments and not lessons:
        return None

    generated_lessons = generate_lessons(lessons, adjustments, year)[month]

    has_any_lesson = False
    for duration in ["30min", "45min", "60min"]:
        generated_lessons[duration] = 0

    # Liczenie lekcji na podstawie ich długości
    for lesson_handler in generated_lessons['Lessons'].values():
        if lesson_handler.status == Statutes.PLANNED or lesson_handler.status == Statutes.NIEOBECNOSC:
            duration_key = f"{str(lesson_handler.duration)[:2]}min"
            if duration_key in generated_lessons:
                generated_lessons[duration_key] += 1
                has_any_lesson = True

    if not has_any_lesson:
        return None

    keys_to_remove = ["Lessons", "Zaplanowana", "Nieobecnosc", "Odwolana - nauczyciel", "Odwolana - 24h przed"]
    for key in keys_to_remove:
        generated_lessons.pop(key, None)

    return generated_lessons


def count_lessons_for_group_in_year(group_id, year):
    lessons = Lesson.objects.filter(
        Q(group_id=group_id) &
        Q(start_time__year__lte=year) &
        (
            (Q(series_end_date__year__gte=year) |
             Q(series_end_date=None))
        )
    )

    adjustments = LessonAdjustment.objects.filter(
        Q(lesson__group_id=group_id) &
        (
                Q(original_lesson_date__year=year) |
                Q(modified_start_time__year=year)
        )
    )

    return generate_lessons(lessons, adjustments, year)


def get_lessons_for_teacher_in_year(teacher_id, year):
    lessons = Lesson.objects.filter(
        Q(teacher_id=teacher_id) &
        Q(start_time__year__lte=year) &
        (
            (Q(series_end_date__year__gte=year) |
             Q(series_end_date=None))
        )
    )

    adjustments = LessonAdjustment.objects.filter(
        Q(teacher_id=teacher_id) &
        (
                Q(original_lesson_date__year=year) |
                Q(modified_start_time__year=year)
        )
    )

    return {'lessons': lessons, 'adjustments': adjustments}


def count_lessons_for_teacher_in_day(teacher_id, year, month, day):
    day_of_month = dj_timezone.make_aware(dj_timezone.datetime(year, month, day))

    lessons = Lesson.objects.filter(
        Q(teacher_id=teacher_id) &
        (
            (
                Q(is_series=False) &
                Q(start_time__year=year) &
                Q(start_time__month=month) &
                Q(start_time__day=day)) |
            (
                Q(is_series=True) &
                Q(start_time__lte=day_of_month) &
                (
                    Q(series_end_date__isnull=True) |
                    Q(series_end_date__gte=day_of_month)
                )
            )
        )
    )

    adjustments = LessonAdjustment.objects.filter(
        Q(lesson__teacher_id=teacher_id) &
        (
            (
                Q(original_lesson_date__year=year) &
                Q(original_lesson_date__month=month) &
                Q(original_lesson_date__day=day)

            ) |
            (
                Q(modified_start_time__year=year) &
                Q(modified_start_time__month=month) &
                Q(modified_start_time__day=day)
            )
        )
    )
    print(adjustments)
    print(lessons)

    generated_lessons = generate_lessons_for_day(lessons, adjustments, day_of_month)
    print(generated_lessons)

    return generated_lessons


def get_lessons_for_location_in_year(location_id, year):
    lessons = Lesson.objects.filter(
        Q(location_id=location_id) &
        Q(start_time__year__lte=year) &
        (
            (Q(series_end_date__year__gte=year) |
             Q(series_end_date=None))
        )
    )

    adjustments = LessonAdjustment.objects.filter(
        Q(location_id=location_id) &
        (
                Q(original_lesson_date__year=year) |
                Q(modified_start_time__year=year)
        )
    )

    return {'lessons': lessons, 'adjustments': adjustments}


def generate_lessons(lessons, adjustments, year):
    current_timezone = dj_timezone.get_current_timezone()

    # get current server date
    current_datetime = datetime.now().astimezone(current_timezone)

    lessons_count_in_months = defaultdict(
        lambda: {Statutes.PLANNED: 0, Statutes.NIEOBECNOSC: 0, Statutes.ODWOLANA_NAUCZYCIEL: 0,
                 Statutes.ODWOLANA_24H_PRZED: 0, 'Lessons': {}})

    # create placeholders for all months
    all_months = range(1, 13)
    for month in all_months:
        lessons_count_in_months[month]

    for lesson in lessons:
        if lesson.is_series:
            current_date = lesson.start_time.date()
            current_date_time = lesson.start_time
            if year != lesson.start_time.year:
                current_date_time = datetime.combine(date(year, 1, 1), lesson.start_time.time())
                if current_date_time.weekday() != lesson.start_time.weekday():
                    weekday_difference = lesson.start_time.weekday() - current_date_time.weekday()
                    current_date_time += timedelta(days=weekday_difference)
                current_date = current_date_time.date()

            if lesson.series_end_date:
                end_date = min(lesson.series_end_date, datetime(year, 12, 31).date())
            else:
                end_date = datetime(year, 12, 31).date()

            while current_date <= end_date:
                if current_date.weekday() == lesson.start_time.weekday():
                    month = current_date.month
                    status = Statutes.PLANNED
                    lessons_count_in_months[month][status] += 1
                    lessons_count_in_months[month]['Lessons'][
                        generate_lesson_dict_key(current_date_time, lesson.id)] = LessonHandler(
                        start_date=current_date,
                        end_date=current_date,
                        start_time=lesson.start_time,
                        end_time=lesson.end_time,
                        lesson_id=lesson.id,
                        description=lesson.description,
                        teacher=lesson.teacher.get_full_name(),
                        student=lesson.student,
                        location=lesson.location.get_full_name()
                    )

                # Przechodzimy do nast\u0119pnego tygodnia
                current_date += timedelta(days=7)
                current_date_time += timedelta(days=7)
        elif lesson.start_time.year == year:
            month = lesson.start_time.month
            status = Statutes.PLANNED
            lessons_count_in_months[month][status] += 1
            lessons_count_in_months[month]['Lessons'][
                generate_lesson_dict_key(lesson.start_time, lesson.id)] = LessonHandler(
                start_date=lesson.start_time.date(),
                end_date=lesson.end_time.date(),
                start_time=lesson.start_time,
                end_time=lesson.end_time,
                lesson_id=lesson.id,
                description=lesson.description,
                teacher=lesson.teacher.get_full_name(),
                student=lesson.student,
                location=lesson.location.get_full_name()
            )

    for adjustment in adjustments:
        month_original_lesson = adjustment.original_lesson_date.month
        month_modified_lesson = adjustment.modified_start_time.month

        original_lesson_datetime = datetime.combine(adjustment.original_lesson_date.date(),
                                                    adjustment.lesson.start_time.time())

        if adjustment.original_lesson_date.year == year:
            lessons_count_in_months[month_original_lesson][Statutes.PLANNED] -= 1
        origan_lesson_key_dict = generate_lesson_dict_key(original_lesson_datetime, adjustment.lesson.id)
        if origan_lesson_key_dict in lessons_count_in_months[month_original_lesson]['Lessons']:
            del lessons_count_in_months[month_original_lesson]['Lessons'][
                generate_lesson_dict_key(original_lesson_datetime, adjustment.lesson.id)]
        status = Statutes.PLANNED

        if adjustment.modified_start_time.year == year:
            lessons_count_in_months[month_modified_lesson][adjustment.status] += 1
            status = adjustment.status

            lessons_count_in_months[month_modified_lesson]['Lessons'][
                generate_lesson_dict_key(adjustment.modified_start_time, 'adj' + str(adjustment.id))] = LessonHandler(
                start_date=adjustment.modified_start_time.date(),
                end_date=adjustment.modified_end_time.date(),
                start_time=adjustment.modified_start_time,
                end_time=adjustment.modified_end_time,
                lesson_id=adjustment.id,
                status=status,
                is_adjustment=True,
                original_date=adjustment.original_lesson_date,
                description=adjustment.lesson.description,
                teacher=adjustment.teacher.get_full_name(),
                student=adjustment.lesson.student,
                location=adjustment.location.get_full_name()
            )

    lessons_count_in_months = dict(sorted(lessons_count_in_months.items()))

    for month, data in lessons_count_in_months.items():
        sorted_lessons = dict(sorted(data['Lessons'].items()))
        lessons_count_in_months[month]['Lessons'] = sorted_lessons
    return lessons_count_in_months


def generate_lessons_for_day(lessons, adjustments, target_date):
    current_timezone = dj_timezone.get_current_timezone()
    lessons_for_day = {
        Statutes.PLANNED: 0,
        Statutes.NIEOBECNOSC: 0,
        Statutes.ODWOLANA_NAUCZYCIEL: 0,
        Statutes.ODWOLANA_24H_PRZED: 0,
        'Lessons': {}
    }

    for lesson in lessons:
        if lesson.is_series:
            # Obliczamy datę i czas dla lekcji cyklicznych
            current_date = lesson.start_time.date()
            current_date_time = lesson.start_time

            # Jeśli seria ma datę zakończenia, sprawdzamy, czy lekcja mieści się w zakresie
            end_date = lesson.series_end_date or date(target_date.year, 12, 31)

            # Sprawdzamy, czy wybrany dzień pasuje do cyklu serii
            while current_date <= end_date:
                if current_date == target_date:
                    status = Statutes.PLANNED
                    lessons_for_day[status] += 1
                    lessons_for_day['Lessons'][generate_lesson_dict_key(current_date_time, lesson.id)] = LessonHandler(
                        start_date=current_date,
                        end_date=current_date,
                        start_time=lesson.start_time,
                        end_time=lesson.end_time,
                        lesson_id=lesson.id,
                        description=lesson.description,
                        teacher=lesson.teacher.get_full_name(),
                        student=lesson.student,
                        location=lesson.location.get_full_name()
                    )
                    break
                # Przechodzimy do następnego tygodnia
                current_date += timedelta(days=7)
                current_date_time += timedelta(days=7)
        else:
            # Lekcje jednorazowe, które przypadają na target_date
            if lesson.start_time.date() == target_date:
                status = Statutes.PLANNED
                lessons_for_day[status] += 1
                lessons_for_day['Lessons'][generate_lesson_dict_key(lesson.start_time, lesson.id)] = LessonHandler(
                    start_date=lesson.start_time.date(),
                    end_date=lesson.end_time.date(),
                    start_time=lesson.start_time,
                    end_time=lesson.end_time,
                    lesson_id=lesson.id,
                    description=lesson.description,
                    teacher=lesson.teacher.get_full_name(),
                    student=lesson.student,
                    location=lesson.location.get_full_name()
                )

    for adjustment in adjustments:
        original_lesson_datetime = datetime.combine(adjustment.original_lesson_date, adjustment.lesson.start_time.time())

        # Sprawdzenie, czy oryginalna data lekcji przypada na target_date
        if adjustment.original_lesson_date == target_date:
            lessons_for_day[Statutes.PLANNED] -= 1
            lessons_for_day['Lessons'].pop(generate_lesson_dict_key(original_lesson_datetime, adjustment.lesson.id), None)

        # Dodanie zmodyfikowanej lekcji, jeśli przypada na target_date
        if adjustment.modified_start_time.date() == target_date:
            status = adjustment.status
            lessons_for_day[status] += 1
            lessons_for_day['Lessons'][generate_lesson_dict_key(adjustment.modified_start_time, 'adj' + str(adjustment.id))] = LessonHandler(
                start_date=adjustment.modified_start_time.date(),
                end_date=adjustment.modified_end_time.date(),
                start_time=adjustment.modified_start_time,
                end_time=adjustment.modified_end_time,
                lesson_id=adjustment.id,
                status=status,
                is_adjustment=True,
                original_date=adjustment.original_lesson_date,
                description=adjustment.lesson.description,
                teacher=adjustment.teacher.get_full_name(),
                student=adjustment.lesson.student,
                location=adjustment.location.get_full_name()
            )

    # Sortowanie lekcji po czasie rozpoczęcia
    lessons_for_day['Lessons'] = dict(sorted(lessons_for_day['Lessons'].items()))
    return lessons_for_day



def create_lesson_adjustment(lesson_form, is_edit=False):
    start_time = lesson_form.cleaned_data['startTime']
    lesson_duration = lesson_form.cleaned_data['lessonDuration']
    lesson_date = lesson_form.cleaned_data['lessonDate']
    original_lesson_date = lesson_form.cleaned_data['originalDate']

    teacher = lesson_form.cleaned_data['teacher']
    location = lesson_form.cleaned_data['location']

    start_datetime = datetime.combine(lesson_date, start_time)
    end_datetime = start_datetime + timedelta(minutes=lesson_duration)

    start_datetime = dj_timezone.make_aware(
        start_datetime,
        dj_timezone.get_current_timezone())

    end_datetime = dj_timezone.make_aware(
        end_datetime,
        dj_timezone.get_current_timezone())
    if not is_edit:
        lesson = Lesson.objects.get(id=lesson_form.cleaned_data['lessonId'])

        original_datetime = dj_timezone.make_aware(
            datetime.combine(original_lesson_date, lesson.start_time.time()),
            dj_timezone.get_current_timezone()
        )

        lesson_adjustment = LessonAdjustment.objects.create(
            lesson_id=lesson_form.cleaned_data['lessonId'],
            modified_start_time=start_datetime,
            modified_end_time=end_datetime,
            original_lesson_date=original_datetime,
            status=lesson_form.cleaned_data['status'],
            teacher_id=teacher,
            location_id=location,
        )
    else:
        lesson_adjustment_id = lesson_form.cleaned_data['lessonId']
        lesson_adjustment = LessonAdjustment.objects.get(id=lesson_adjustment_id)
        lesson_adjustment.modified_start_time = start_datetime
        lesson_adjustment.modified_end_time = end_datetime
        lesson_adjustment.status = lesson_form.cleaned_data['status']
        lesson_adjustment.teacher_id = teacher
        lesson_adjustment.location_id = location

        lesson_adjustment.save()
