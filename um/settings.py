import os
from ast import literal_eval
from pathlib import Path

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = literal_eval(os.environ.get("DEBUG", "False"))

DOMAIN = "www.um-osrs.com"

if DEBUG:
    ip_address = os.environ.get("IP_ADDRESS")
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", ip_address]
    INTERNAL_IPS = ["localhost", "127.0.0.1", ip_address]
else:
    # Production Security
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 3600  # in seconds ; that's 1 hour, ya pootz
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    ALLOWED_HOSTS = [DOMAIN]

INSTALLED_APPS = [
    "um.admin.UMAdminConfig",
    "django.contrib.auth",
    "polymorphic",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "account",
    "admin_auto_filters",
    "django_browser_reload",
    "formtools",
    "main",
    "achievements",
    "dragonstone",
    "storages",
    "tailwind",
    "theme",
    "notifications",
]

if DEBUG:
    INSTALLED_APPS += [
        "django_extensions",
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
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "um.urls"

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

WSGI_APPLICATION = "um.wsgi.application"

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("LOCAL_DB_NAME"),
            "USER": os.environ.get("LOCAL_DB_USERNAME"),
            "PASSWORD": os.environ.get("LOCAL_DB_PASSWORD"),
            "HOST": "localhost",
            "PORT": "",
        }
    }
else:
    DATABASES = {"default": dj_database_url.config(conn_max_age=600)}

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

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_HOST = os.environ.get("STATIC_HOST")
STATIC_URL = STATIC_HOST + "/static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

if DEBUG:
    MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
    MEDIA_URL = "media/"
if not DEBUG:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    # AWS settings
    AWS_S3_ACCESS_KEY_ID = os.environ.get("AWS_S3_ACCESS_KEY_ID")
    AWS_S3_SECRET_ACCESS_KEY = os.environ.get("AWS_S3_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TAILWIND_APP_NAME = "theme"

if not DEBUG:
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[
            DjangoIntegration(),
        ],
        traces_sample_rate=0,
        send_default_pii=True,
    )

# Email settings
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")

MAX_COL_LOG = int(os.environ.get("MAX_COL_LOG"))

UM_PB_DISCORD_WEBHOOK_URL = os.environ.get(
    "UM_PB_DISCORD_WEBHOOK_URL"
)  # for posting discord embeds to the #um-pb-leaderboards channel!

WOM_API_KEY = os.environ.get("WOM_API_KEY")
