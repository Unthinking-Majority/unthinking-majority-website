from django.db import models
from django.utils import timezone


class Bounty(models.Model):
    title = models.CharField(max_length=128, default="")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    board = models.ForeignKey("main.Board", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="bounty/image/")
    prize_pool = models.PositiveIntegerField(
        default=0, help_text="Total amount of gp in the prize pool."
    )

    class Meta:
        ordering = ["-start_date"]

    @classmethod
    def get_current_bounty(cls):
        today = timezone.now()
        try:
            current_bounty = cls.objects.get(start_date__lt=today, end_date__gt=today)
        except cls.DoesNotExist:
            return None
        return current_bounty

    def get_submissions(self):
        return self.board.sort_submissions().filter(
            date__gte=self.start_date, date__lte=self.end_date
        )

    def get_most_improved(self):
        raise NotImplementedError

    def get_most_submissions(self):
        raise NotImplementedError
