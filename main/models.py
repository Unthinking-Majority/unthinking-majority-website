from django.db import models


class Board(models.Model):
    BOSS, MINIGAME = range(2)
    BOARD_CHOICES = (
        (BOSS, 'Boss'),
        (MINIGAME, 'Minigame'),
    )
    TIME, OTHER = range(2)
    METRIC_CHOICES = (
        (TIME, 'Time'),
        (OTHER, 'Other'),
    )
    name = models.CharField(max_length=256)
    icon = models.ImageField(upload_to='board/icons/', null=True, blank=True)
    type = models.IntegerField(choices=BOARD_CHOICES, default=BOSS)
    metric = models.IntegerField(choices=METRIC_CHOICES, default=TIME)
    category = models.ForeignKey('main.BoardCategory', on_delete=models.CASCADE, related_name='boards')
    slug = models.SlugField()

    def __str__(self):
        return self.name


class BoardCategory(models.Model):
    name = models.CharField(max_length=256)

    class Meta:
        verbose_name = 'Board Category'
        verbose_name_plural = 'Board Categories'

    def __str__(self):
        return self.name


class Pet(models.Model):
    name = models.CharField(max_length=256)
    icon = models.ImageField(upload_to='pet/icons/', null=True, blank=True)

    def __str__(self):
        return self.name


class Submission(models.Model):
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    board = models.ForeignKey('main.Board', on_delete=models.CASCADE, related_name='submissions')
    value = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    proof = models.ImageField(upload_to='submission/proof/', null=True, blank=True)

    def __str__(self):
        return f'{self.account.name} - {self.board} - {self.date} - {self.value}'
