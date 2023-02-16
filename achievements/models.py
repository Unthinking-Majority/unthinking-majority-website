import json
from datetime import datetime

import requests
from django.conf import settings
from django.contrib.postgres.aggregates import StringAgg
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F

from achievements import CA_CHOICES
from main import TIME, INTEGER
from main import managers
from um.functions import get_file_path


class BaseSubmission(models.Model):
    UPLOAD_TO = 'submission/proof/'

    proof = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    notes = models.TextField(blank=True)
    accepted = models.BooleanField(null=True)
    date = models.DateTimeField(default=datetime.now, null=True, blank=True)

    objects = managers.SubmissionQueryset.as_manager()

    child_models = (
        'recordsubmission',
        'petsubmission',
        'collogsubmission',
        'casubmission'
    )

    class Meta:
        ordering = [F('date').desc(nulls_last=True)]
        verbose_name = 'Base Submission'
        verbose_name_plural = 'All Submissions'

    def type_display(self):
        """
        Call the type_display() method from the corresponding child instance of this base submission
        """
        for child_model in self.child_models:
            child_obj = getattr(self, child_model, None)
            if child_obj:
                return child_obj.type_display()

    def value_display(self):
        """
        Call the value_display() method from the corresponding child instance of this base submission
        """
        for child_model in self.child_models:
            child_obj = getattr(self, child_model, None)
            if child_obj:
                return child_obj.value_display()

    def get_child_instance(self):
        """
        Return the corresponding child instance of this base submission
        """
        for child_model in self.child_models:
            child_obj = getattr(self, child_model, None)
            if child_obj:
                return child_obj


class RecordSubmission(BaseSubmission):
    accounts = models.ManyToManyField('account.Account')
    board = models.ForeignKey('main.Board', on_delete=models.CASCADE, related_name='submissions')
    value = models.DecimalField(max_digits=7, decimal_places=2)

    __original_accepted = None

    class Meta:
        verbose_name = 'Record Submission'
        verbose_name_plural = 'Record Submissions'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_accepted = self.accepted

    def save(self, *args, **kwargs):
        super(RecordSubmission, self).save(*args, **kwargs)
        if self.accepted and self.accepted != self.__original_accepted:
            # post to discord um pb webhook the newly accepted submission! only for record submissions
            data = json.dumps({'embeds': [self.create_embed()]})
            requests.post(
                settings.UM_PB_DISCORD_WEBHOOK_URL,
                data=data,
                headers={'Content-Type': 'application/json'}
            )

    def type_display(self):
        return self.board.name

    def value_display(self):
        if self.board.content.metric == TIME:
            minutes = int(self.value // 60)
            seconds = self.value % 60
            return f'{minutes}:{seconds:05}'
        else:
            return int(self.value) if self.board.content.metric == INTEGER else self.value

    def get_rank(self):
        ordering = self.board.content.ordering

        active_accounts_submissions = self.board.submissions.active_submissions().accepted()

        # annotate the teams (accounts values) into a string so we can order by unique teams of accounts and value
        annotated_submissions = active_accounts_submissions.annotate(
            accounts_str=StringAgg('accounts__name', delimiter=',', ordering='accounts__name')
        ).order_by('accounts_str', f'{ordering}value')

        # grab the first submission for each team (which is the best, since we ordered by value above)
        submissions = {}
        for submission in annotated_submissions:
            if submission.accounts_str not in submissions.keys():
                submissions[submission.accounts_str] = submission.id
        submissions = self.__class__.objects.filter(id__in=submissions.values()).order_by(f'{ordering}value', 'date')

        for rank, submission in enumerate(submissions):
            if submission.id == self.id:
                return rank + 1

    def create_embed(self):
        """
        Create json discord embed.
        """
        fields = [
            {
                'name': 'Board',
                'value': self.board.name,
            },
            {
                'name': 'User(s)',
                'value': ', '.join(self.accounts.values_list('name', flat=True)),
            },
            {
                'name': self.board.content.metric_name,
                'value': self.value_display(),
                'inline': True,
            },
            {
                'name': 'Date',
                'value': f'{self.date:%b %d, %Y}',
                'inline': True,
            },
            {
                'name': 'Rank',
                'value': str(self.get_rank()) or '-',
                'inline': True,
            },
        ]
        if self.notes:
            fields.append(
                {
                    'name': 'Notes',
                    'value': self.notes,
                }
            )

        embed = {
            'color': 0x0099FF,
            'title': 'New Submission',
            'fields': fields,
            'url': f'https://{settings.DOMAIN}{self.board.content.leaderboard_url()}',
        }

        if not settings.DEBUG:
            embed['image'] = {'url': self.proof.url}

        return embed


class PetSubmission(BaseSubmission):
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    pet = models.ForeignKey('main.Pet', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Pet Submission'
        verbose_name_plural = 'Pet Submissions'

    def type_display(self):
        return 'Pet'

    def value_display(self):
        return self.pet.name


class ColLogSubmission(BaseSubmission):
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    col_logs = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(settings.MAX_COL_LOG)])

    class Meta:
        verbose_name = 'Collection Log Submission'
        verbose_name_plural = 'Collection Log Submissions'

    def type_display(self):
        return 'Collection Logs'

    def value_display(self):
        return f'{self.col_logs}/{settings.MAX_COL_LOG}'


class CASubmission(BaseSubmission):
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    ca_tier = models.IntegerField(choices=CA_CHOICES, default=None, null=True, blank=True, verbose_name='Combat Achievement Tier')

    class Meta:
        verbose_name = 'Combat Achievement Submission'
        verbose_name_plural = 'Combat Achievement Submissions'

    def type_display(self):
        return 'Combat Achievement'

    def value_display(self):
        return self.get_ca_tier_display()
