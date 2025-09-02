from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.apps import apps
from django.conf import settings


class Command(BaseCommand):
    help = "Synchronize group permissions based on the GROUP_PERMISSIONS dictionary."

    def handle(self, *args, **kwargs):
        print("Synchronizing group permissions...")
        for group_name, perms in settings.GROUP_PERMISSIONS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for perm_name in perms:
                app_label, codename = perm_name.split('.')
                try:
                    permission = Permission.objects.get(
                        content_type__app_label=app_label, codename=codename
                    )
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"Permission '{perm_name}' does not exist. Please check the GROUP_PERMISSIONS configuration."
                    ))
            self.stdout.write(self.style.SUCCESS(f"Permissions for group '{group_name}' synchronized."))
