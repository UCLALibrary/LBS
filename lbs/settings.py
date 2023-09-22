"""
Django settings for lbs project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from django.contrib.messages import constants as messages
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG")
# Helm charts pass "false" instead of Python False, and
# Python "false" is True...
if DEBUG in ["false", "False"]:
    DEBUG = False

# Define the list of allowed hosts to connect to this application
# This is passed in via the environment variable DJANGO_ALLOWED_HOSTS
# which is a string - but ALLOWED_HOSTS requires a list
ALLOWED_HOSTS = list(os.getenv("DJANGO_ALLOWED_HOSTS").split(","))

# Django 4 may require this, at least in our deployment environment.
CSRF_TRUSTED_ORIGINS = list(os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS").split(","))

# Application definition

INSTALLED_APPS = [
    # Enable whitenoise in development per http://whitenoise.evans.io/en/stable/django.html
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "qdb",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lbs.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "lbs.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DJANGO_DB_BACKEND"),
        "NAME": os.getenv("DJANGO_DB_NAME"),
        "USER": os.getenv("DJANGO_DB_USER"),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD"),
        "HOST": os.getenv("DJANGO_DB_HOST"),
        "PORT": os.getenv("DJANGO_DB_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Los_Angeles"

USE_I18N = True


USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# Django will add this URL, and serve static files from here
STATIC_URL = "/static/"
# Where on the file system should Django find our custom static files?
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
# Where will all static files - our custom + Django's?
# This matters only when not using runserver, and using collectstaticfiles.
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# There is a timing issue with Whitenoise that is described here:
# https://github.com/evansd/whitenoise/issues/215
# The work around suggested is to check for the existence of the
# static root directory, and if doesn't exist yet then create it
if not os.path.isdir(STATIC_ROOT):
    os.makedirs(STATIC_ROOT, mode=0o755)

# Improved caching with whitenoise when running in production.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGOUT_REDIRECT_URL = "/admin"

MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

# Email config
# Backend does not currently matter, as the app's legacy sender.py
# uses smtplib directly, bypassing Django
# But this will be helpful if/when that code is updated to use Django.
EMAIL_BACKEND = os.getenv("DJANGO_EMAIL_BACKEND")
