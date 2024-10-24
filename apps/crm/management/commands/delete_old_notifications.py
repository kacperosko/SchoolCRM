from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.crm.models import Notification


class Command(BaseCommand):
    help = 'Delete notifications older than 30 days'

    def handle(self, *args, **options):
        # Calculate the threshold date for old notifications
        threshold_date = timezone.now() - timezone.timedelta(days=30)
        # Delete notifications older than the threshold date
        try:
            deleted, _ = Notification.objects.filter(created_at__lt=threshold_date).delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted} old notifications'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(e))

