from time import monotonic

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from main.models import Settings

__all__ = ["config"]


class Config:
    """
    Config wrapper for main.models.Settings to allow simpler and more elegant use of the Settings model.
    All settings are loaded in one query and cached per process for CACHE_SECONDS. Saving a Settings row clears
    the cache in the process that saved it; other processes pick the change up when their cache expires.
    """

    CACHE_SECONDS = 60

    def __init__(self):
        self._values = None
        self._loaded_at = 0

    def clear(self):
        self._values = None

    def _load(self):
        if self._values is None or monotonic() - self._loaded_at > self.CACHE_SECONDS:
            self._values = dict(Settings.objects.values_list("key", "value"))
            self._loaded_at = monotonic()
        return self._values

    def __getattr__(self, key):
        if key.startswith("_"):
            raise AttributeError(key)
        try:
            value = self._load()[key]
        except KeyError:
            raise AttributeError(key)
        if value.isnumeric():
            value = int(value)
        return value


config = Config()


@receiver(post_save, sender=Settings)
@receiver(post_delete, sender=Settings)
def clear_config_cache(sender, **kwargs):
    config.clear()
