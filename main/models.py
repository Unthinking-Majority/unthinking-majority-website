from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from main import managers


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
    board = models.ForeignKey('main.Board', on_delete=models.CASCADE, related_name='submissions')
    value = models.DecimalField(max_digits=6, decimal_places=2)
    proof = models.ImageField(upload_to='submission/proof/', null=True, blank=True)
    accepted = models.BooleanField(null=True)
    date = models.DateField(auto_now_add=True)

    objects = managers.SubmissionManger()

    def __str__(self):
        return f'account here - {self.board} - {self.date} - {self.value}'

    def value_display(self):
        if self.board.metric == self.board.TIME:
            minutes = int(self.value // 60)
            seconds = self.value % 60
            return f"{minutes}:{seconds}"
        else:
            return self.value
