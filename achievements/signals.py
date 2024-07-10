from django.db.models.signals import post_save
from django.dispatch import receiver

from achievements import models

__all__ = ["submission_created"]


@receiver(post_save, sender=models.RecordSubmission)
@receiver(post_save, sender=models.PetSubmission)
@receiver(post_save, sender=models.ColLogSubmission)
@receiver(post_save, sender=models.CASubmission)
def submission_created(sender, instance, created, *args, **kwargs):
    if created:
        instance.on_creation()
