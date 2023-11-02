from django.apps import AppConfig

from constance.apps import ConstanceConfig


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"


class CustomConstanceConfig(ConstanceConfig):
    verbose_name = "Settings"
    verbose_name_plural = "Settings"
