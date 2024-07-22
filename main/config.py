from main.models import Settings

__all__ = ["config"]


class Config:
    """
    Config wrapper for main.models.Settings to allow simpler and more elegant use of the Settings model.
    """

    def __getattr__(self, key):
        try:
            value = Settings.objects.get(key=key).value
            if value.isnumeric():
                value = int(value)
            return value
        except Settings.DoesNotExist:
            raise AttributeError(key)


config = Config()
