import json
import os
import uuid
from datetime import datetime

import requests
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F
from django.urls import reverse

from main import METRIC_CHOICES, CA_CHOICES, SUBMISSION_TYPES, RECORD, PET, COL_LOG, CA, TIME, INTEGER
from main import managers


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join(instance.UPLOAD_TO, f'{uuid.uuid4()}.{ext}')


class Board(models.Model):
    name = models.CharField(max_length=256, unique=True)
    parent = models.ForeignKey('main.ParentBoard', on_delete=models.CASCADE, related_name='boards')
    team_size = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(8)])
    flex_order = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(12)],
                                             help_text='Order on leaderboard page. Empty values will appear last (order is then defined by team size). Allowed numbers are 1 - 12.')

    class Meta:
        ordering = ['team_size', 'name']

    def __str__(self):
        return self.name


class ParentBoard(models.Model):
    UPLOAD_TO = 'board/icons/'

    name = models.CharField(max_length=256, unique=True)
    category = models.ForeignKey('main.BoardCategory', on_delete=models.CASCADE, related_name='parent_boards')
    metric = models.IntegerField(choices=METRIC_CHOICES, default=TIME)
    metric_name = models.CharField(max_length=128, default='Time')
    slug = models.SlugField(unique=True)
    icon = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    ordering = models.CharField(choices=(('-', 'Descending'), ('', 'Ascending')), default='', max_length=1,
                                help_text='Order of values when showing submission from child boards.')
    order = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(12)],
                                        help_text='Order in navbar. Empty values will appear last (order is then defined by alphabetical order of name). Allowed numbers are 1 - 12.')

    class Meta:
        verbose_name = 'Parent Board'
        verbose_name_plural = 'Parent Boards'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def leaderboard_url(self):
        return reverse('leaderboard', kwargs={'board_category': self.category.slug, 'parent_board_name': self.slug})


class BoardCategory(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Board Category'
        verbose_name_plural = 'Board Categories'

    def __str__(self):
        return self.name


class Pet(models.Model):
    UPLOAD_TO = 'pet/icons/'

    name = models.CharField(max_length=256, unique=True)
    icon = models.ImageField(upload_to=get_file_path, null=True, blank=True)

    def __str__(self):
        return self.name


class Submission(models.Model):
    UPLOAD_TO = 'submission/proof/'

    accounts = models.ManyToManyField('account.Account')
    type = models.IntegerField(choices=SUBMISSION_TYPES, default=RECORD)
    board = models.ForeignKey('main.Board', on_delete=models.CASCADE, related_name='submissions', blank=True, null=True)
    value = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    pet = models.ForeignKey('main.Pet', on_delete=models.CASCADE, related_name='submissions', blank=True, null=True)
    ca_tier = models.IntegerField(choices=CA_CHOICES, default=None, null=True, blank=True)
    proof = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    notes = models.TextField(blank=True)
    accepted = models.BooleanField(null=True)
    date = models.DateTimeField(default=datetime.now, null=True, blank=True)

    objects = managers.SubmissionQueryset.as_manager()

    __original_accepted = None

    class Meta:
        ordering = [F('date').desc(nulls_last=True)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_accepted = self.accepted

    def save(self, *args, **kwargs):
        super(Submission, self).save(*args, **kwargs)
        if self.accepted and self.accepted != self.__original_accepted and self.type == RECORD:
            # post to discord um pb webhook the newly accepted submission! only for record submissions
            data = json.dumps({'embeds': [self.create_embed()]})
            request = requests.post(
                settings.UM_PB_DISCORD_WEBHOOK_URL,
                data=data,
                headers={'Content-Type': 'application/json'}
            )

    def __str__(self):
        accounts = ', '.join(self.accounts.values_list('name', flat=True))
        return f'{accounts} - {self.board} - {self.value}'

    def value_display(self):
        if self.type == CA:
            return self.get_ca_tier_display()

        if self.type == PET:
            return self.pet.name

        if not self.value:
            return None

        if self.type == RECORD:
            if self.board.parent.metric == TIME:
                minutes = int(self.value // 60)
                seconds = self.value % 60
                return f"{minutes}:{seconds:05}"
            else:
                return int(self.value) if self.board.parent.metric == INTEGER else self.value

        if self.type == COL_LOG:
            return f'{int(self.value)}/{settings.MAX_COL_LOG}'

    def type_display(self):
        if self.type == RECORD:
            return self.board.name
        else:
            return self.get_type_display()

    def get_rank(self):
        submissions = self.board.submissions.accepted().order_by(
            f'{self.board.parent.ordering}value',
            'date'
        )
        print(submissions)
        for rank, submission in enumerate(submissions):
            print(rank, submission)
            if submission.id == self.id:
                print('gottem')
                return rank + 1

    def create_embed(self):
        """
        Create json discord embed. Only supported for submission type RECORD.
        """

        if self.type != RECORD:
            return {}

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
                'name': self.board.parent.metric_name,
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
                'value': str(self.get_rank()),
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
            'url': f'https://www.um-osrs.com{self.board.parent.leaderboard_url()}',
        }

        if not settings.DEBUG:
            embed['image'] = {'url': self.proof.url}

        return embed
