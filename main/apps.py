from constance.apps import ConstanceConfig
from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"


class CustomConstanceConfig(ConstanceConfig):
    verbose_name = "Settings"
    verbose_name_plural = "Settings"

    def ready(self):
        super().ready()
        from main import signals
