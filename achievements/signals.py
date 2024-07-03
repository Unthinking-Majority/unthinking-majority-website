from django.db.models.signals import pre_save
from django.dispatch import receiver
from achievements.models impo

__all__ = ["submission_created"]


@receiver(pre_save)
def submission_created(sender, key, old_value, new_value, **kwargs):
    pass
