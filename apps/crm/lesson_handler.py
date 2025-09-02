from datetime import datetime, timedelta
from .models import LessonStatutes, Event
from collections import defaultdict
from django.db.models import Q
from django.db import transaction


def generate_lesson_dict(lessons):

    lessons_count_in_months = defaultdict(
        lambda: {LessonStatutes.ZAPLANOWANA.value: 0, LessonStatutes.NIEOBECNOSC.value: 0, LessonStatutes.ODWOLANA_NAUCZYCIEL.value: 0,
                 LessonStatutes.ODWOLANA_24H_PRZED.value: 0, 'Lessons': {}})
    all_months = range(1, 13)

    for month in all_months:
        lessons_count_in_months[month]

    for lesson in lessons.order_by('event_date'):
        lesson_key = lesson.event_date.strftime('%d-%m-%Y') + "_" + lesson.start_time.strftime('%H:%M')
        while lesson_key in lessons_count_in_months[lesson.event_date.month]['Lessons']:
            lesson_key += "x"

        lessons_count_in_months[lesson.event_date.month]['Lessons'][lesson_key] = lesson.to_dict()
        lessons_count_in_months[lesson.event_date.month][lesson.status] += 1

    lessons_count_in_months = dict(sorted(lessons_count_in_months.items()))

    for month, data in lessons_count_in_months.items():
        sorted_lessons = dict(sorted(data['Lessons'].items()))
        lessons_count_in_months[month]['Lessons'] = sorted_lessons

    return lessons_count_in_months


def get_today_teacher_lessons(teacher_id, lesson_date):
    lessons = Event.objects.filter(event_date=lesson_date, teacher_id=teacher_id).prefetch_related('attendance_list_event')
    return lessons


def get_student_lessons_in_month(student_id, month, year):
    lessons = Event.objects.filter(lesson_definition__student_id=student_id, event_date__month=month, event_date__year=year)
    return generate_lesson_dict_key(lessons)


def get_student_lessons_in_year(student_id, year):
    lessons = Event.objects.filter(lesson_definition__student_id=student_id, event_date__year=year)
    return generate_lesson_dict(lessons)

def get_group_lessons_in_year(group_id, year):
    lessons = Event.objects.filter(lesson_definition__group_id=group_id, event_date__year=year)
    return generate_lesson_dict(lessons)


def get_location_lessons_in_year(location_id, year):
    lessons = Event.objects.filter(location_id=location_id, event_date__year=year)
    return generate_lesson_dict(lessons)


def get_teacher_lessons_in_year(teacher_id, year):
    lessons = Event.objects.filter(teacher_id=teacher_id, event_date__year=year)
    return generate_lesson_dict(lessons)


def generate_lesson_dict_key(start_time: datetime, lesson_id):
    return start_time.strftime("%d_%m_%Y-%H:%M") + "_" + str(lesson_id)


def count_lessons_for_student_in_month(student_id, year, month):
    lessons = Event.objects.filter(
        Q(lesson_definition__student_id=student_id) &
        (
            Q(event_date__year=year) &
            Q(event_date__month=month)
        )
    )

    if not lessons:
        return None

    # generated_lessons = generate_lessons(lessons, adjustments, year)[month]
    counted_lessons = {}
    has_any_lesson = False
    for duration in ["30min", "45min", "60min"]:
        counted_lessons[duration] = 0

    # Liczenie lekcji na podstawie ich długości
    for lesson in lessons:
        if lesson.status == LessonStatutes.ZAPLANOWANA or lesson.status == LessonStatutes.NIEOBECNOSC:
            duration_key = f"{str(lesson.duration)}min"
            if duration_key in counted_lessons:
                counted_lessons[duration_key] += 1
                has_any_lesson = True

    if not has_any_lesson:
        return None

    return counted_lessons


@transaction.atomic
def update_lesson(event, form_data, edit_mode, old_dates):
    """
    Aktualizuje pojedynczą lekcję oraz ewentualnie całą serię w zależności od edit_mode.
    """

    # update pojedynczego eventu
    updated_event = form_data.save()

    if edit_mode == 'single':
        return

    # --- logika dla edit_mode == 'series' ---
    new_date = updated_event.event_date
    new_start_time = updated_event.start_time

    event.original_lesson_datetime = datetime.combine(new_date, new_start_time)
    event.save()

    # czy data lub godzina się zmieniły
    is_shift = (old_dates.get('old_date') != new_date) or (old_dates.get('old_start_time') != new_start_time)

    # znajdź wszystkie kolejne lekcje z tej serii
    affected_lessons = Event.objects.filter(
        lesson_definition=event.lesson_definition,
        original_lesson_datetime__gt=old_dates.get('old_original_datetime')
    ).order_by('original_lesson_datetime')

    print(len(affected_lessons))

    if is_shift:
        print('is shift')
        lessons_to_update = []
        for lesson in affected_lessons:
            # ile tygodni różnicy było między aktualizowaną lekcją a aktualnie przetwarzaną
            weeks_diff = (lesson.original_lesson_datetime.date() - old_dates.get('old_date')).days // 7

            # budujemy nowy termin lekcji względem nowej daty:
            new_event_date = new_date + timedelta(weeks=weeks_diff)
            new_original = datetime.combine(new_event_date, new_start_time)

            lesson.original_lesson_datetime = new_original
            lesson.event_date = new_event_date
            lesson.start_time = new_start_time

            lesson.end_time = (datetime.combine(new_event_date, new_start_time)
                               + timedelta(minutes=lesson.duration)).time()

            lessons_to_update.append(lesson)

        # batchowa aktualizacja
        Event.objects.bulk_update(
            lessons_to_update,
            ['original_lesson_datetime', 'event_date', 'start_time', 'end_time']
        )

        # aktualizujemy hurtowo pozostałe dane (bez przesuwania)
    affected_lessons.update(
        teacher=updated_event.teacher,
        location=updated_event.location,
        status=updated_event.status,
        description=updated_event.description
    )
