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
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "10.0.0.211"]
    INTERNAL_IPS = ["localhost", "127.0.0.1"]
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
    "constance",
    "um.admin.UMAdminConfig",
    "django.contrib.auth",
    "polymorphic",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "rest_framework",
    "rest_framework.authtoken",
    "modelcluster",
    "taggit",
    "account",
    "admin_auto_filters",
    "formtools",
    "notifications",
    "main",
    "achievements",
    "dragonstone",
    "storages",
    "tailwind",
    "theme",
    "bounty",
    "django_filters",
]

if DEBUG:
    INSTALLED_APPS += [
        "django_extensions",
        "django_browser_reload",
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
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

if DEBUG:
    MIDDLEWARE += [
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
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

if DEBUG:
    MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
    MEDIA_URL = "media/"

if not DEBUG:
    STORAGES["default"] = {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"}
    # AWS settings
    AWS_S3_ACCESS_KEY_ID = os.environ.get("AWS_S3_ACCESS_KEY_ID")
    AWS_S3_SECRET_ACCESS_KEY = os.environ.get("AWS_S3_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN")
    AWS_S3_FILE_OVERWRITE = False

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

MAX_COL_LOG = int(os.environ.get("MAX_COL_LOG"))

UM_PB_DISCORD_WEBHOOK_URL = os.environ.get(
    "UM_PB_DISCORD_WEBHOOK_URL"
)  # for posting discord embeds to the #um-pb-leaderboards channel!
BOUNTY_DISCORD_WEBHOOK_URL = os.environ.get(
    "BOUNTY_DISCORD_WEBHOOK_URL"
)  # for posting discord embeds to the #bounty channel during Bounty events!

WOM_API_KEY = os.environ.get("WOM_API_KEY")

# Wagtail settings
WAGTAIL_SITE_NAME = "Unthinking Majority"
WAGTAILADMIN_BASE_URL = "https://www.um-osrs.com"
WAGTAILIMAGES_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp", "svg"]
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # i.e. 20MB

DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000

OSRS_PLAYER_HISCORES_API = os.environ.get("OSRS_PLAYER_HISCORES_API")

# REST Settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissions",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
}
if DEBUG:
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] += [
        "rest_framework.authentication.SessionAuthentication",
    ]
