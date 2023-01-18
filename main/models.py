import os
import uuid
from datetime import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from main import METRIC_CHOICES, CA_CHOICES, SUBMISSION_TYPES, RECORD, PET, COL_LOG, CA, TIME, INTEGER
from main import managers


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join(instance.UPLOAD_TO, f'{uuid.uuid4()}.{ext}')


class Board(models.Model):
    name = models.CharField(max_length=256, unique=True)
    parent = models.ForeignKey('main.ParentBoard', on_delete=models.CASCADE, related_name='boards')
    team_size = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(8)])

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

    class Meta:
        verbose_name = 'Parent Board'
        verbose_name_plural = 'Parent Boards'
        ordering = ['name']

    def __str__(self):
        return self.name


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

    class Meta:
        ordering = ['-date']

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
