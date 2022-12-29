from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.db import models

from main import managers
from main import SUBMISSION_TYPES, RECORD, PET, COL_LOG


class Board(models.Model):
    TIME, INTEGER, DECIMAL = range(3)
    METRIC_CHOICES = (
        (TIME, 'Time'),
        (INTEGER, 'Integer'),
        (DECIMAL, 'Decimal'),
    )
    name = models.CharField(max_length=256)
    category = models.ForeignKey('main.BoardCategory', on_delete=models.CASCADE, related_name='boards')
    metric = models.IntegerField(choices=METRIC_CHOICES, default=TIME)
    metric_name = models.CharField(max_length=128, default='Time')
    max_team_size = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(8)])
    icon = models.ImageField(upload_to='board/icons/', null=True, blank=True)
    slug = models.SlugField(unique=True)

    class Meta:
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
    name = models.CharField(max_length=256, unique=True)
    icon = models.ImageField(upload_to='pet/icons/', null=True, blank=True)

    def __str__(self):
        return self.name


class Submission(models.Model):
    accounts = models.ManyToManyField('account.Account')
    type = models.IntegerField(choices=SUBMISSION_TYPES, default=RECORD)
    board = models.ForeignKey('main.Board', on_delete=models.CASCADE, related_name='submissions', blank=True, null=True)
    value = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    pet = models.ForeignKey('main.Pet', on_delete=models.CASCADE, related_name='submissions', blank=True, null=True)
    proof = models.ImageField(upload_to='submission/proof/', null=True, blank=True)
    notes = models.TextField(blank=True)
    accepted = models.BooleanField(null=True)
    date = models.DateField(auto_now_add=True)

    objects = managers.SubmissionQueryset.as_manager()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'account here - {self.board} - {self.date} - {self.value}'

    def value_display(self):
        if self.type == RECORD:
            minutes = int(self.value // 60)
            seconds = self.value % 60
            return f"{minutes}:{seconds}"
        elif self.type == PET:
            return self.pet.name
        elif self.type == COL_LOG:
            return f'{int(self.value)}/{settings.MAX_COL_LOG}'

    def type_display(self):
        if self.type == RECORD:
            return self.board.name
        elif self.type == PET:
            return 'Pet'
        elif self.type == COL_LOG:
            return 'Collection Log'
