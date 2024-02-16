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
    "main.apps.CustomConstanceConfig",
    "um.admin.UMAdminConfig",
    "django.contrib.auth",
    "polymorphic",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
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

WOM_API_KEY = os.environ.get("WOM_API_KEY")

if not DEBUG:
    CONSTANCE_REDIS_CONNECTION = os.environ.get("REDIS_URL")
CONSTANCE_SUPERUSER_ONLY = False
CONSTANCE_CONFIG = {
    "DRAGONSTONE_POINTS_THRESHOLD": (40, "Dragonstone Points Threshold"),
    "DRAGONSTONE_EXPIRATION_PERIOD": (180, "Dragonstone Expiration Period (in days)"),
    "PVM_SPLIT_POINTS_MAX": (25, "Maximum Points Allowed from PVM Splits"),
    "RECRUITER_PTS": (2, "Dragonstone Recruiter Points"),
    "SOTM_FIRST_PTS": (3, "Skill of the Month First Place Points"),
    "SOTM_SECOND_PTS": (2, "Skill of the Month Second Points"),
    "SOTM_THIRD_PTS": (1, "Skill of the Month Third Points"),
    "PVM_SPLIT_EASY_PTS": (0, "Pvm Splits Easy Points"),
    "PVM_SPLIT_MEDIUM_PTS": (1, "Pvm Splits Medium Points"),
    "PVM_SPLIT_HARD_PTS": (1, "Pvm Splits Hard Points"),
    "PVM_SPLIT_VERY_HARD_PTS": (2, "Pvm Splits Very Hard Points"),
    "MENTOR_EASY_PTS": (1, "Mentor Easy Points"),
    "MENTOR_MEDIUM_PTS": (2, "Mentor Medium Points"),
    "MENTOR_HARD_PTS": (3, "Mentor Hard Points"),
    "MENTOR_VERY_HARD_PTS": (4, "Mentor Very Hard Points"),
    "EVENT_MINOR_HOSTS_PTS": (5, "Event Minor Hosts Points"),
    "EVENT_MINOR_PARTICIPANTS_PTS": (2, "Event Minor Participants Points"),
    "EVENT_MINOR_DONORS_PTS": (0, "Event Minor Donors Points"),
    "EVENT_MENTOR_PARTICIPANTS_PTS": (2, "Event Mentor Participants Points"),
    "EVENT_MAJOR_PARTICIPANTS_PTS": (5, "Event Major Participants Points"),
    "EVENT_MAJOR_DONORS_PTS": (2, "Event Major Donors Points"),
    "EVENT_OTHER_HOSTS_PTS": (3, "Event Other Hosts Points"),
    "EVENT_OTHER_PARTICIPANTS_PTS": (1, "Event Other Participants Points"),
    "EVENT_OTHER_DONORS_PTS": (0, "Event Other Donors Points"),
    "EVENT_MENTOR_DONORS_PTS": (0, "Event Mentor Donors Points"),
    "EVENT_MENTOR_HOSTS_PTS": (5, "Event Mentor Hosts Points"),
    "EVENT_MAJOR_HOSTS_PTS": (15, "Event Major Hosts Points"),
    "NEW_MEMBER_RAID_PTS": (2, "New Member Raid Points"),
    "FIRST_PLACE_PTS": (10, "Points for 1st Place"),
    "SECOND_PLACE_PTS": (5, "Points for 2nd Place"),
    "THIRD_PLACE_PTS": (3, "Points for 3rd Place"),
    "FOURTH_PLACE_PTS": (2, "Points for 4th Place"),
    "FIFTH_PLACE_PTS": (1, "Points for 5th Place"),
}

# Wagtail settings
WAGTAIL_SITE_NAME = "Unthinking Majority"
WAGTAILADMIN_BASE_URL = "https://www.um-osrs.com"
WAGTAILIMAGES_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp", "svg"]
WAGTAILIMAGES_MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # i.e. 20MB

DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000

OSRS_PLAYER_HISCORES_API = os.environ.get("OSRS_PLAYER_HISCORES_API")
