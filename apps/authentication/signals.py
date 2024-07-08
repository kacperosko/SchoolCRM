from django.dispatch import receiver
from django.db.models.signals import pre_save
from .models import User

@receiver(pre_save, sender=User)
def record_password_change(sender, **kwargs):
    user = kwargs.get('instance', None)
    if user:
        new_password = user.password
        try:
            old_password = User.objects.get(pk=user.pk).password
        except User.DoesNotExist:
            old_password = None

        if new_password != old_password:
            try:
                send_mail(
                    subject="Twoje hasło zostało zmienione",
                    message=f"Hej {user.first_name}, dostajesz tego maila ponieważ Twoje hasło na {SITE_URL} zostało zmienione.\nJeśli nie zmieniałeś/aś hasła niezwłocznie skontaktuj się z administratorem strony",
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(e)
