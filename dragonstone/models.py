from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from main.models import BaseSubmission


class RecruitmentSubmission(BaseSubmission):
    UPLOAD_TO = 'dragonstone/recruitment/proof/'
    recruiter = models.ForeignKey('account.Account', on_delete=models.CASCADE, related_name='recruited')
    recruited = models.ForeignKey('account.Account', on_delete=models.CASCADE, related_name='recruited_by')

    class Meta:
        verbose_name = 'Recruitment Submission'
        verbose_name_plural = 'Recruitment Submissions'

    def type_display(self):
        return 'Recruitment Submission'

    def value_display(self):
        return f'{self.recruiter} recruited {self.recruited}'


class SotMSubmission(BaseSubmission):
    UPLOAD_TO = 'dragonstone/sotm/proof/'
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    rank = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])

    class Meta:
        verbose_name = 'Skill of the Month Submission'
        verbose_name_plural = 'Skill of the Month Submissions'

    def type_display(self):
        return 'Skill of the Month Submission'

    def value_display(self):
        nth = {
            1: '1st',
            2: '2nd',
            3: '3rd'
        }
        return f'{self.account.name} - {nth[self.rank]}'


class PVMSplitSubmission(BaseSubmission):
    UPLOAD_TO = 'dragonstone/pvm/proof/'
    accounts = models.ManyToManyField('account.Account')
    content = models.ForeignKey('main.Content', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'PVM Split Submission'
        verbose_name_plural = 'PVM Split Submissions'

    def type_display(self):
        return 'PVM Split Submission'

    def value_display(self):
        return f'{", ".join(self.accounts.values_list("name", flat=True))} - {self.content.name}'


class MentorSubmission(BaseSubmission):
    UPLOAD_TO = 'dragonstone/mentor/proof/'
    mentors = models.ManyToManyField('account.Account', related_name='mentored')
    learners = models.ManyToManyField('account.Account', related_name='mentor_learners')
    content = models.ForeignKey('account.Account', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Mentor Submission'
        verbose_name_plural = 'Mentor Submissions'

    def type_display(self):
        return 'Mentor Submission'

    def value_display(self):
        return f'Mentorship by {", ".join(self.mentors.values_list("name", flat=True))} for {self.content.name}'


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

    class Meta:
        verbose_name = 'Event Submission'
        verbose_name_plural = 'Event Submissions'

    def type_display(self):
        return 'Event Submission'

    def value_display(self):
        return f'Event hosted by {", ".join(self.hosts.values_list("name", flat=True))}'
