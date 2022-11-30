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
    type = models.IntegerField(choices=BOARD_CHOICES, default=BOSS)
    metric = models.IntegerField(choices=METRIC_CHOICES, default=TIME)

    def __str__(self):
        return self.name


class Submission(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    board = models.ForeignKey('main.Board', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.board} - {self.date} - {self.value}'
