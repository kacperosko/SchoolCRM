from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Note, WatchRecord, Notification, Student
from django.utils import timezone
from apps.authentication.middleware.current_user_middleware import get_current_user


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
                    message=f'{user.get_full_name()} zaktualizował/a notatkę dla {instance.content_object} : {instance.content[:16]}{dots}',
                    content_object=watch_record.content_object,
                    object_id=watch_record.object_id
                )
            )
    if len(notifications) > 0:
        print('bulk create notifications')
        Notification.objects.bulk_create(notifications)


@receiver(pre_save, sender=Student)
def set_created_by_modified_by(sender, instance, **kwargs):
    user = get_current_user()
    if not instance.pk:  # Check if the record is new
        print('$$$ CREATE student', instance.first_name, 'user', user)
        instance.created_date = timezone.now()
        instance.created_by = user
    else:
        print('$$$ UPDATE student', instance.first_name, 'user', user)
    instance.modified_date = timezone.now()
    instance.modified_by = user
