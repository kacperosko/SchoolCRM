from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Note, WatchRecord, Notification, Student, Group, AttendanceList, LessonDefinition, Event, EventType, LessonStatutes
from django.utils import timezone
from apps.authentication.middleware.current_user_middleware import get_current_user
from datetime import timedelta, date, datetime
import calendar
from django.utils.timezone import make_aware

@receiver(post_save, sender=LessonDefinition)
def generate_lesson_events(sender, instance, created, **kwargs):
    if created:  # Wygeneruj lekcje tylko dla nowo dodanej definicji
        current_date = instance.lesson_date

        # Oblicz docelowy miesiąc i rok
        target_month = (instance.lesson_date.month + 6 - 1) % 12 + 1
        target_year = instance.lesson_date.year + (instance.lesson_date.month + 6 - 1) // 12

        # Pobierz ostatni dzień docelowego miesiąca
        last_day = calendar.monthrange(target_year, target_month)[1]

        # Ustawienie stop_date na ostatni dzień miesiąca za 6 miesięcy
        calculated_stop_date = date(target_year, target_month, last_day)

        # Jeśli istnieje series_end_date, wybierz wcześniejszą z dat
        stop_date = min(instance.series_end_date, calculated_stop_date) if instance.series_end_date else calculated_stop_date

        print('SIGNALS generate_lesson_events')
        print('series_end_date -> ' + str(instance.series_end_date))
        print('stop_date -> ' + str(stop_date))
        print('target_month -> ' + str(target_month))
        print('target_year -> ' + str(target_year))
        print('is_series -> ' + str(instance.is_series))

        lessons = []
        while current_date <= stop_date:

            lessons.append(
                Event(
                    event_type=EventType.LESSON,
                    lesson_definition=instance,
                    status=LessonStatutes.ZAPLANOWANA,
                    event_date=current_date,
                    original_lesson_datetime=make_aware(datetime.combine(current_date, instance.start_time)),
                    start_time=instance.start_time,
                    end_time=(datetime.combine(date.today(), instance.start_time) + timedelta(minutes=instance.duration)).time(),
                    duration=instance.duration,
                    teacher=instance.teacher,
                    location=instance.location,
                )
            )
            # Przesuwaj datę co tydzień, jeśli to seria
            if instance.is_series:
                current_date += timedelta(weeks=1)
            else:
                break  # Bez serii tylko jedno wydarzenie

        Event.objects.bulk_create(lessons)


def get_record_watchers(content_type, object_id):
    return WatchRecord.objects.filter(
        content_type=content_type,
        object_id=object_id
    )


@receiver(post_save, sender=Note)
def create_notifications(sender, instance, created, **kwargs):
    watch_records = get_record_watchers(instance.content_type, instance.object_id)
    notifications = []
    if created:
        for watch_record in watch_records:
            if watch_record.user.id == instance.created_by.id:
                continue  # skip creating notification for user who triggered signals
            dots = "..." if len(instance.content) > 16 else ""
            notifications.append(
                Notification(
                    user=watch_record.user,
                    message=f'Nowa notatka dodana dla {instance.content_object} : {instance.content[:16]}{dots}',
                    content_object=watch_record.content_object,
                    object_id=watch_record.object_id
                )
            )
    else:
        print('update note')
        user = get_current_user()
        print('user', user.get_full_name())
        for watch_record in watch_records:
            dots = "..." if len(instance.content) > 16 else ""
            notifications.append(
                Notification(
                    user=watch_record.user,
                    message=f'{user.get_full_name()} zaktualizowa\u0142/a notatk\u0119 dla {instance.content_object} : {instance.content[:16]}{dots}',
                    content_object=watch_record.content_object,
                    object_id=watch_record.object_id
                )
            )
    if len(notifications) > 0:
        print('bulk create notifications')
        Notification.objects.bulk_create(notifications)


def set_created_by_modified_by(sender, instance):
    print('signals set_created_by_modified_by')
    user = get_current_user()
    if not instance.pk:  # Check if the record is new
        instance.created_date = timezone.now()
        instance.created_by = user
    instance.modified_date = timezone.now()
    instance.modified_by = user


@receiver(pre_save, sender=Student)
def student_signal(sender, instance, **kwargs):
    set_created_by_modified_by(sender, instance)


@receiver(pre_save, sender=Group)
def group_signal(sender, instance, **kwargs):
    set_created_by_modified_by(sender, instance)


@receiver(pre_save, sender=AttendanceList)
def attendance_list_signal(sender, instance, **kwargs):
    set_created_by_modified_by(sender, instance)
