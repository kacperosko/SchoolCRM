from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    # default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'

    def ready(self):
        import apps.authentication.signals
        from django.core.management import call_command
        call_command('sync_group_permissions')
