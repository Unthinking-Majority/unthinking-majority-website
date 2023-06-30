from django.db import models


class Bounty(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    board = models.ForeignKey('main.Board', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='bounty/image/')

    @classmethod
    def current_bounty():
        raise NotImplementedError

    def get_submissions(self):
        # return self.board.submissions.filter()
        raise NotImplementedError

    def get_most_improved(self):
        raise NotImplementedError
    
    def get_most_submissions(self):
        raise NotImplementedError
