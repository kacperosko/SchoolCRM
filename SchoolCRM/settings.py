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
DEBUG = False

ALLOWED_HOSTS = ['*']
SITE_URL = 'warsztat-muzyczny.kacperosko.hmcloud.pl'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60  # (60 * 60 seconds = 60 minutes)
SESSION_SAVE_EVERY_REQUEST = True

SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SECURE_SSL_REDIRECT = False

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

DEFAULT_FROM_EMAIL = 'biuro@warsztat-muzyczny.kacperosko.hmcloud.pl'
EMAIL_HOST = 'mx1.hitme.net.pl'
EMAIL_HOST_PORT = 465
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'biuro@warsztat-muzyczny.kacperosko.hmcloud.pl'
EMAIL_HOST_PASSWORD = 'K@cper123!'


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
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'warsztat6_warsztat_muzyczny',
        'USER': 'warsztat6_warsztat_muzyczny',
        'PASSWORD': 'fygdeX-8worwu-tifdov',
        'HOST': 'localhost',
        'PORT': '',
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
STATIC_ROOT = '/home/warsztat6/domains/warsztat-muzyczny.kacperosko.hmcloud.pl/warsztat-crm/static'
MEDIA_ROOT = '/home/warsztat6/domains/warsztat-muzyczny.kacperosko.hmcloud.pl/warsztat-crm//media'


STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'apps/static'),
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
