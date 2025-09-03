from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-uta=i!_i25%tc1y*h!!w1r$o+s7tj354vg30hlf8!w42d0mz+%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
SITE_URL = 'warsztat-muzyczny.kacperosko.hmcloud.pl'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60  # (60 * 60 seconds = 60 minutes)
SESSION_SAVE_EVERY_REQUEST = True

SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # apps
    'apps.crm',
    'apps.authentication',
]

AUTH_USER_MODEL = 'authentication.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.authentication.middleware.login_required_middleware.LoginRequiredMiddleware',
    'apps.authentication.middleware.current_user_middleware.CurrentUserMiddleware',
    # 'apps.crm.middleware.notifications_middleware.UnreadNotificationsMiddleware'
]
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
ROOT_URLCONF = 'SchoolCRM.urls'

# Email sending configuration

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FROM_EMAIL = 'biuro@system-crm.pl'



TEMPLATE_DIR = os.path.join(CORE_DIR, "templates")  # ROOT dir for _templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SchoolCRM.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'crmdb'),
        'USER': os.environ.get('DB_USER', 'crmuser'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'crmpassword'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGOUT_REDIRECT_URL = "/login"
LOGIN_URL = '/login'

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'pl'
DEFAULT_CHARSET = 'utf-8'

TIME_ZONE = 'Europe/Warsaw'
USE_TZ = True

USE_I18N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'apps/static'),
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


GROUP_PERMISSIONS = {
    "Nauczyciel": [
        "crm.view_attendancelist",
        "crm.add_attendancelist",
        "crm.view_group",
        "crm.view_lessondefinition",
        "crm.view_event",
        "crm.view_location",
        "crm.view_note",
        "crm.change_note",
        "crm.add_note",
        "crm.view_person",
        "crm.view_student",
    ],
    "Kierownik": [
        "crm.view_attendancelist",
        "crm.change_attendancelist",
        "crm.add_attendancelist",
        "crm.delete_attendancelist",
        "crm.view_group",
        "crm.change_group",
        "crm.add_group",
        "crm.delete_group",
        "crm.view_groupstudent",
        "crm.change_groupstudent",
        "crm.add_groupstudent",
        "crm.delete_groupstudent",
        "crm.view_lessondefinition",
        "crm.change_lessondefinition",
        "crm.add_lessondefinition",
        "crm.delete_lessondefinition",
        "crm.view_event",
        "crm.change_event",
        "crm.add_event",
        "crm.delete_event",
        "crm.view_location",
        "crm.change_location",
        "crm.add_location",
        "crm.delete_location",
        "crm.view_note",
        "crm.change_note",
        "crm.add_note",
        "crm.delete_note",
        "crm.view_person",
        "crm.change_person",
        "crm.add_person",
        "crm.delete_person",
        "crm.view_student",
        "crm.change_student",
        "crm.add_student",
        "crm.delete_student",
        "crm.view_invoice",
        "crm.change_invoice",
        "crm.add_invoice",
        "crm.delete_invoice",
        "crm.view_invoiceitem",
        "crm.change_invoiceitem",
        "crm.add_invoiceitem",
        "crm.delete_invoiceitem",
        "auth.view_user",
        "auth.change_user",
        "auth.add_user"
    ],
    "Administrator": [] # Po wybraniu roli administratora Django automatycznie ustawia flage is_superuser nadajaca wymagane uprawnienia
}
