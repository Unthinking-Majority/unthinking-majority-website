import os
import uuid
from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join(instance.UPLOAD_TO, f'{uuid.uuid4()}.{ext}')


class BaseSubmission(models.Model):
    proof = models.ImageField(upload_to=get_file_path)
    notes = models.TextField(blank=True)
    accepted = models.BooleanField(null=True)
    date = models.DateTimeField(default=datetime.now)


class RecruitmentSubmission(BaseSubmission):
    UPLOAD_TO = 'dragonstone/recruitment/proof/'
    recruiter = models.ForeignKey('account.Account', on_delete=models.CASCADE, related_name='a')
    recruited = models.ForeignKey('account.Account', on_delete=models.CASCADE, related_name='b')


class SotMSubmission(BaseSubmission):
    UPLOAD_TO = 'dragonstone/sotm/proof/'
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    rank = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])


class PVMSplitSubmission(BaseSubmission):
    UPLOAD_TO = 'dragonstone/pvm/proof/'
    accounts = models.ManyToManyField('account.Account')
    content = models.ForeignKey('main.Content', on_delete=models.CASCADE)


class MentorSubmission(BaseSubmission):
    UPLOAD_TO = 'dragonstone/mentor/proof/'
    mentors = models.ManyToManyField('account.Account', related_name='mentored')
    learners = models.ManyToManyField('account.Account', related_name='mentor_learners')
    content = models.ForeignKey('account.Account', on_delete=models.CASCADE)


class EventSubmission(BaseSubmission):
    UPLOAD_TO = 'dragonstone/event/proof/'
    PVM, SKILLING, MAJOR, OTHER = range(4)
    EVENT_CHOICES = (
        (PVM, 'PVM'),
        (SKILLING, 'Skilling'),
        (MAJOR, 'Major Event'),
        (OTHER, 'Other'),
    )
    hosts = models.ManyToManyField('account.Account', related_name='events_hosted')
    participants = models.ManyToManyField('account.Account', related_name='events_participated')
    donators = models.ManyToManyField('account.Account', related_name='events_donated')
    type = models.IntegerField(choices=EVENT_CHOICES)
