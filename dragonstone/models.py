from datetime import timedelta, datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Value, Case, When, F, Q, Sum
from django.utils import timezone

from dragonstone import EVENT_CHOICES, PVM, SKILLING, MAJOR, OTHER
from main import EASY, MEDIUM, HARD, VERY_HARD
from main import managers
from um.functions import get_file_path

three_months_ago = timezone.now().date() - timedelta(days=90)


class DragonstoneBaseSubmission(models.Model):
    UPLOAD_TO = 'dragonstone/submission/proof/'

    proof = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    notes = models.TextField(blank=True)
    accepted = models.BooleanField(null=True)
    date = models.DateTimeField(default=datetime.now, null=True, blank=True)

    objects = managers.SubmissionQueryset.as_manager()

    child_models = (
        'recruitmentsubmission',
        'sotmsubmission',
        'pvmsplitsubmission',
        'mentorsubmission',
        'eventsubmission',
    )

    class Meta:
        ordering = [F('date').desc(nulls_last=True)]

    def type_display(self):
        """
        Call the type_display() method from the corresponding child instance of this base submission
        """
        for child_model in self.child_models:
            child_obj = getattr(self, child_model, None)
            if child_obj:
                return child_obj.type_display()

    def value_display(self):
        """
        Call the value_display() method from the corresponding child instance of this base submission
        """
        for child_model in self.child_models:
            child_obj = getattr(self, child_model, None)
            if child_obj:
                return child_obj.value_display()

    def get_child_instance(self):
        """
        Return the corresponding child instance of this base submission
        """
        for child_model in self.child_models:
            child_obj = getattr(self, child_model, None)
            if child_obj:
                return child_obj


class RecruitmentSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = 'dragonstone/recruitment/proof/'
    RECRUITER_PTS = 2

    recruiter = models.ForeignKey('account.Account', on_delete=models.CASCADE, related_name='recruited')
    recruited = models.ForeignKey('account.Account', on_delete=models.CASCADE, related_name='recruited_by')

    class Meta:
        verbose_name = 'Recruitment Submission'
        verbose_name_plural = 'Recruitment Submissions'

    @classmethod
    def annotate_dragonstone_pts(cls, account=None):
        """
        Return a list containing (account, dragonstone_pts) values.
        If account is provided, return only the dragonstone points for that account.
        Only consider submission made within the last 3 months.
        """
        if account:
            return cls.objects.accepted().filter(date__gte=three_months_ago, recruiter=account).annotate(
                dragonstone_pts=Value(cls.RECRUITER_PTS),
            ).aggregate(total_dragonstone_pts=Sum('dragonstone_pts'))['total_dragonstone_pts'] or 0
        return list(cls.objects.accepted().filter(date__gte=three_months_ago).annotate(
            dragonstone_pts=Value(cls.RECRUITER_PTS),
            account=F('recruiter'),
        ).values('account', 'dragonstone_pts'))

    def type_display(self):
        return 'Recruitment Submission'

    def value_display(self):
        return f'{self.recruiter} recruited {self.recruited}'


class SotMSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = 'dragonstone/sotm/proof/'
    FIRST_PTS = 3
    SECONDS_PTS = 2
    THIRD_PTS = 1

    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    rank = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])

    class Meta:
        verbose_name = 'Skill of the Month Submission'
        verbose_name_plural = 'Skill of the Month Submissions'

    @classmethod
    def annotate_dragonstone_pts(cls, account=None):
        """
        Return a list containing (account, dragonstone_pts) values.
        Only consider submission made within the last 3 months.
        """
        if account:
            return cls.objects.accepted().filter(date__gte=three_months_ago, account=account).annotate(
                dragonstone_pts=Case(
                    When(rank=1, then=cls.FIRST_PTS),
                    When(rank=2, then=cls.SECONDS_PTS),
                    When(rank=3, then=cls.THIRD_PTS),
                )
            ).aggregate(total_dragonstone_pts=Sum('dragonstone_pts'))['total_dragonstone_pts'] or 0
        return list(cls.objects.accepted().filter(date__gte=three_months_ago).annotate(
            dragonstone_pts=Case(
                When(rank=1, then=cls.FIRST_PTS),
                When(rank=2, then=cls.SECONDS_PTS),
                When(rank=3, then=cls.THIRD_PTS),
            )
        ).values('account', 'dragonstone_pts'))

    def type_display(self):
        return 'Skill of the Month Submission'

    def value_display(self):
        nth = {
            1: '1st',
            2: '2nd',
            3: '3rd',
        }
        return f'{self.account.name} - {nth[self.rank]}'


class PVMSplitSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = 'dragonstone/pvm/proof/'
    MEDIUM_PTS = 1
    HARD_PTS = 1
    VERY_HARD_PTS = 2

    accounts = models.ManyToManyField('account.Account')
    content = models.ForeignKey('main.Content', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'PVM Split Submission'
        verbose_name_plural = 'PVM Split Submissions'

    @classmethod
    def annotate_dragonstone_pts(cls, account=None):
        """
        Return a list containing (account, dragonstone_pts) values.
        Only consider submission made within the last 3 months.
        """
        if account:
            return cls.objects.accepted().filter(date__gte=three_months_ago, accounts=account).annotate(
                dragonstone_pts=Case(
                    When(content__difficulty=MEDIUM, then=cls.MEDIUM_PTS),
                    When(content__difficulty=HARD, then=cls.HARD_PTS),
                    When(content__difficulty=VERY_HARD, then=cls.VERY_HARD_PTS),
                ),
            ).aggregate(total_dragonstone_pts=Sum('dragonstone_pts'))['total_dragonstone_pts'] or 0
        return list(cls.objects.accepted().filter(date__gte=three_months_ago).annotate(
            dragonstone_pts=Case(
                When(content__difficulty=MEDIUM, then=cls.MEDIUM_PTS),
                When(content__difficulty=HARD, then=cls.HARD_PTS),
                When(content__difficulty=VERY_HARD, then=cls.VERY_HARD_PTS),
            ),
            account=F('accounts'),
        ).values('account', 'dragonstone_pts'))

    def type_display(self):
        return 'PVM Split Submission'

    def value_display(self):
        return f'{", ".join(self.accounts.values_list("name", flat=True))} - {self.content.name}'


class MentorSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = 'dragonstone/mentor/proof/'
    EASY_PTS = 1
    MEDIUM_PTS = 2
    HARD_PTS = 3
    VERY_HARD_PTS = 4

    mentors = models.ManyToManyField('account.Account', related_name='mentored')
    learners = models.ManyToManyField('account.Account', related_name='mentor_learners')
    content = models.ForeignKey('main.Content', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Mentor Submission'
        verbose_name_plural = 'Mentor Submissions'

    @classmethod
    def annotate_dragonstone_pts(cls, account=None):
        """
        Return a list containing (account, dragonstone_pts) values.
        Only consider submission made within the last 3 months.
        """
        if account:
            return cls.objects.accepted().filter(date__gte=three_months_ago).annotate(
                dragonstone_pts=Case(
                    When(content__difficulty=EASY, then=cls.EASY_PTS),
                    When(content__difficulty=MEDIUM, then=cls.MEDIUM_PTS),
                    When(content__difficulty=HARD, then=cls.HARD_PTS),
                    When(content__difficulty=VERY_HARD, then=cls.VERY_HARD_PTS),
                ),
            ).aggregate(total_dragonstone_pts=Sum('dragonstone_pts'))['total_dragonstone_pts'] or 0
        return list(cls.objects.accepted().filter(date__gte=three_months_ago).annotate(
            dragonstone_pts=Case(
                When(content__difficulty=EASY, then=cls.EASY_PTS),
                When(content__difficulty=MEDIUM, then=cls.MEDIUM_PTS),
                When(content__difficulty=HARD, then=cls.HARD_PTS),
                When(content__difficulty=VERY_HARD, then=cls.VERY_HARD_PTS),
            ),
            account=F('mentors'),
        ).values('account', 'dragonstone_pts'))

    def type_display(self):
        return 'Mentor Submission'

    def value_display(self):
        return f'Mentorship by {", ".join(self.mentors.values_list("name", flat=True))} for {self.content.name}'


class EventSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = 'dragonstone/event/proof/'
    MINOR_HOSTS_PTS = 5
    MINOR_PARTICIPANTS_PTS = 2
    MAJOR_HOSTS_PTS = 15
    MAJOR_PARTICIPANTS_PTS = 5
    MAJOR_DONORS_PTS = 2
    OTHER_HOSTS_PTS = 3
    OTHER_PARTICIPANTS_PTS = 1

    hosts = models.ManyToManyField('account.Account', related_name='events_hosted')
    participants = models.ManyToManyField('account.Account', related_name='events_participated')
    donors = models.ManyToManyField('account.Account', related_name='events_donated')
    type = models.IntegerField(choices=EVENT_CHOICES)

    class Meta:
        verbose_name = 'Event Submission'
        verbose_name_plural = 'Event Submissions'

    @classmethod
    def annotate_dragonstone_pts(cls, account=None):
        """
        Return a list containing (account, dragonstone_pts) values.
        Only consider submission made within the last 3 months.
        """
        if account:
            hosts_pts = cls.objects.accepted().filter(date__gte=three_months_ago).annotate(
                dragonstone_pts=Case(
                    When(Q(type=PVM) | Q(type=SKILLING), then=cls.MINOR_HOSTS_PTS),
                    When(type=MAJOR, then=cls.MAJOR_HOSTS_PTS),
                    When(type=OTHER, then=cls.OTHER_HOSTS_PTS),
                ),
            ).aggregate(total_dragonstone_pts=Sum('dragonstone_pts'))['total_dragonstone_pts'] or 0

            participants_pts = cls.objects.accepted().filter(date__gte=three_months_ago).annotate(
                dragonstone_pts=Case(
                    When(Q(type=PVM) | Q(type=SKILLING), then=cls.MINOR_PARTICIPANTS_PTS),
                    When(type=MAJOR, then=cls.MAJOR_PARTICIPANTS_PTS),
                    When(type=OTHER, then=cls.OTHER_PARTICIPANTS_PTS),
                ),
            ).aggregate(total_dragonstone_pts=Sum('dragonstone_pts'))['total_dragonstone_pts'] or 0

            donors_pts = cls.objects.accepted().filter(date__gte=three_months_ago).annotate(
                dragonstone_pts=Case(
                    When(type=MAJOR, then=cls.MAJOR_DONORS_PTS),
                ),
            ).aggregate(total_dragonstone_pts=Sum('dragonstone_pts'))['total_dragonstone_pts'] or 0
        else:
            hosts_pts = list(cls.objects.accepted().filter(date__gte=three_months_ago).annotate(
                dragonstone_pts=Case(
                    When(Q(type=PVM) | Q(type=SKILLING), then=cls.MINOR_HOSTS_PTS),
                    When(type=MAJOR, then=cls.MAJOR_HOSTS_PTS),
                    When(type=OTHER, then=cls.OTHER_HOSTS_PTS),
                ),
                account=F('hosts'),
            ).values('account', 'dragonstone_pts'))

            participants_pts = list(cls.objects.accepted().filter(date__gte=three_months_ago).annotate(
                dragonstone_pts=Case(
                    When(Q(type=PVM) | Q(type=SKILLING), then=cls.MINOR_PARTICIPANTS_PTS),
                    When(type=MAJOR, then=cls.MAJOR_PARTICIPANTS_PTS),
                    When(type=OTHER, then=cls.OTHER_PARTICIPANTS_PTS),
                ),
                account=F('participants'),
            ).values('account', 'dragonstone_pts'))

            donors_pts = list(cls.objects.accepted().filter(date__gte=three_months_ago).annotate(
                dragonstone_pts=Case(
                    When(type=MAJOR, then=cls.MAJOR_DONORS_PTS),
                ),
                account=F('donors'),
            ).values('account', 'dragonstone_pts'))
        return hosts_pts + participants_pts + donors_pts

    def type_display(self):
        return 'Event Submission'

    def value_display(self):
        return f'Event hosted by {", ".join(self.hosts.values_list("name", flat=True))}'
