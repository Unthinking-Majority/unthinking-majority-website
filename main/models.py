from datetime import date

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from main import SUBMISSION_TYPES, RECORD, PET, COL_LOG
from main import managers


class Board(models.Model):
    TIME, INTEGER, DECIMAL = range(3)
    METRIC_CHOICES = (
        (TIME, 'Time'),
        (INTEGER, 'Integer'),
        (DECIMAL, 'Decimal'),
    )
    name = models.CharField(max_length=256)
    parent = models.ForeignKey('main.ParentBoard', on_delete=models.CASCADE, related_name='boards')
    metric = models.IntegerField(choices=METRIC_CHOICES, default=TIME)
    metric_name = models.CharField(max_length=128, default='Time')
    max_team_size = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(8)])

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ParentBoard(models.Model):
    name = models.CharField(max_length=256)
    category = models.ForeignKey('main.BoardCategory', on_delete=models.CASCADE, related_name='parent_boards')
    slug = models.SlugField(unique=True)
    icon = models.ImageField(upload_to='board/icons/', null=True, blank=True)

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
    date = models.DateField(default=date.today)

    objects = managers.SubmissionQueryset.as_manager()

    __original_accepted = None

    class Meta:
        ordering = ['-date']

    def __str__(self):
        accounts = ', '.join(self.accounts.values_list('name', flat=True))
        return f'{accounts} - {self.board} - {self.date} - {self.value}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_accepted = self.accepted

    def save(self, *args, **kwargs):
        if self.accepted != self.__original_accepted:
            # status of submission has changed
            if self.type == COL_LOG:
                # update collection log based off of status change
                if self.accepted:
                    account = self.accounts.first()
                    account.col_logs = self.value
                    account.save()
        return super(Submission, self).save(*args, **kwargs)

    def value_display(self):
        if self.type == RECORD:
            if self.board.metric == self.board.TIME:
                try:
                    minutes = int(self.value // 60)
                    seconds = self.value % 60
                    return f"{minutes}:{seconds:05}"
                except TypeError:
                    return ""
            elif self.board.metric == self.board.INTEGER:
                return int(self.value)
            else:
                return self.value
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
