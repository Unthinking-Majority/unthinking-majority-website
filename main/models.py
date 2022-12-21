from django.db import models

from main import managers


class Board(models.Model):
    BOSS, MINIGAME = range(2)
    BOARD_CHOICES = (
        (BOSS, 'Boss'),
        (MINIGAME, 'Minigame'),
    )
    TIME, OTHER, TEARS, OVERALL_TIME, CHALLENGE_TIME = range(5)
    METRIC_CHOICES = (
        (TIME, 'Time'),
        (OTHER, 'Other'),
        (TEARS, 'Tears'),
        (OVERALL_TIME, 'Overall Time'),
        (CHALLENGE_TIME, 'Challenge Time'),
    )
    name = models.CharField(max_length=256)
    icon = models.ImageField(upload_to='board/icons/', null=True, blank=True)
    type = models.IntegerField(choices=BOARD_CHOICES, default=BOSS)
    metric = models.IntegerField(choices=METRIC_CHOICES, default=TIME)
    category = models.ForeignKey('main.BoardCategory', on_delete=models.CASCADE, related_name='boards')
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
        if self.board.metric in (self.board.TIME, self.board.OVERALL_TIME, self.board.CHALLENGE_TIME):
            minutes = int(self.value // 60)
            seconds = self.value % 60
            return f"{minutes}:{seconds}"
        else:
            return self.value
