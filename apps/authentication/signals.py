from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User
from SchoolCRM.settings import SITE_URL, EMAIL_HOST_USER
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse


@receiver(post_save, sender=User)
def send_password_reset_email(sender, instance, created, **kwargs):
    user = instance
    if created:  # Tylko dla nowo utworzonych użytkowników
        try:
            # Generowanie tokenu i linku do resetu hasła
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
            full_reset_url = f'{SITE_URL}{reset_url}'

            # Wysłanie e-maila z linkiem do resetu hasła
            subject = "Witaj w SzkolniQ"
            message = (
                f"Hej {user.first_name},\n\n"
                f"W systemie SzkolniQ, dla Warsztat Muzyczny, zostało utworzone dla Ciebie konto. "
                f"Aby się zalogować, ustaw swoje hasło używając poniższego linku:\n"
                f"{full_reset_url}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            print('Błąd podczas wysyłania e-maila: ', e)
    else:
        new_password = user.password
        try:
            old_password = User.objects.get(pk=user.pk).password
        except User.DoesNotExist:
            old_password = None

        if new_password != old_password:
            try:
                send_mail(
                    subject="Twoje haslo zostalo zmienione",
                    message=f"Hej {user.first_name}, dostajesz tego maila poniewa\u017C"
                            f" Twoje has\u0142o na {SITE_URL} zosta\u0142o zmienione.\nJe\u015Bli nie zmienia\u0142e\u015B/a\u015B has\u0142a niezw\u0142ocznie skontaktuj si\u0119 z administratorem strony",
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print('changes pwd email error:', e)
