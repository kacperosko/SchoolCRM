from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User
from SchoolCRM.settings import SITE_URL, EMAIL_HOST_USER
from django.core.mail import send_mail


@receiver(post_save, sender=User)
def record_password_change(sender, instance, created, **kwargs):
    user = instance
    print('start signal USER')
    if user:
        print('user exist')
        if created:
            print('user created')
            try:
                send_mail(
                    subject="Witaj w Warsztat CRM",
                    message=f"Hej {user.first_name}, w systemie Warsztat CRM zostalo utworzone dla Ciebie konto. Aby sie zalogowac zresetuj haslo uzywajac ponizszego linku:\nwww.{SITE_URL}/password-reset/",
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print('Error sending create email record_password_change', e)
        else:
            print('user updated')
            new_password = user.password
            try:
                old_password = User.objects.get(pk=user.pk).password
            except User.DoesNotExist:
                old_password = None

            if new_password != old_password:
                try:
                    print("zmieniono haslo, leci mail")
                    send_mail(
                        subject="Twoje haslo zostalo zmienione",
                        message=f"Hej {user.first_name}, dostajesz tego maila ponieważ"
                                f" Twoje hasło na {SITE_URL} zostało zmienione.\nJeśli nie zmieniałeś/aś hasła niezwłocznie skontaktuj się z administratorem strony",
                        from_email=EMAIL_HOST_USER,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print('changes pwd email error:', e)
