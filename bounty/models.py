from django.db import models
from django.utils import timezone


class Bounty(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    board = models.ForeignKey("main.Board", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="bounty/image/")

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
        return (
            self.board.submissions.active_submissions()
            .accepted()
            .filter(date__gte=self.start_date, date__lte=self.end_date)
        )

    def get_most_improved(self):
        raise NotImplementedError

    def get_most_submissions(self):
        raise NotImplementedError
