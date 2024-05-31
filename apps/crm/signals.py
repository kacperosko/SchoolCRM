from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Note, WatchRecord, Notification


@receiver(post_save, sender=Note)
def create_notifications(sender, instance, created, **kwargs):
    if created:
        watch_records = WatchRecord.objects.filter(
            content_type=instance.content_type,
            object_id=instance.object_id
        )

        for watch_record in watch_records:
            if watch_record.user.id == instance.created_by.id:
                continue  # skip creating notification for user who triggered signals
            dots = "..." if len(instance.content) > 16 else ""
            Notification.objects.create(
                user=watch_record.user,
                message=f'Nowa notatka dodana dla {instance.content_object} : {instance.content[:16]}{dots}',
                content_object=watch_record.content_object,
                object_id=watch_record.object_id

            )
