from datetime import timedelta, datetime
from django.core.validators import MinValueValidator

from django.db import models
from django.db.models import Value, Case, When, F, Q, Sum
from django.utils import timezone

from dragonstone import EVENT_CHOICES, PVM, SKILLING, MAJOR, OTHER, EVENT_MENTOR
from main import EASY, MEDIUM, HARD, VERY_HARD
from main import managers
from main.models import Settings
from um.functions import get_file_path

expiration_period = timezone.now().date() - timedelta(days=180)


class DragonstoneBaseSubmission(models.Model):
    UPLOAD_TO = "dragonstone/submission/proof/"

    proof = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    notes = models.TextField(blank=True)
    denial_notes = models.TextField(
        blank=True, help_text="Only need to fill out if submission is denied."
    )
    accepted = models.BooleanField(null=True)
    date = models.DateTimeField(default=datetime.now, null=True, blank=True)

    objects = managers.SubmissionQueryset.as_manager()

    child_models = (
        "recruitmentsubmission",
        "sotmsubmission",
        "pvmsplitsubmission",
        "mentorsubmission",
        "eventsubmission",
        "freeformsubmission",
    )

    class Meta:
        ordering = [F("date").desc(nulls_last=True)]
        verbose_name = "Dragonstone Base Submission"
        verbose_name_plural = "All Dragonstone Submissions"

    @classmethod
    def filter_all_submissions_by_account(cls, account):
        # filter for all submission objects inheriting from BaseSubmission which the given account was a part of
        freeform_subs = FreeformSubmission.objects.filter(account=account).values("pk")
        recruitment_subs = RecruitmentSubmission.objects.filter(
            recruiter=account
        ).values("pk")
        sotm_subs = SotMSubmission.objects.filter(account=account).values("pk")
        pvm_split_subs = PVMSplitSubmission.objects.filter(accounts=account).values(
            "pk"
        )
        mentor_subs = MentorSubmission.objects.filter(
            Q(mentors=account) | Q(learners=account)
        )
        event_subs = EventSubmission.objects.filter(
            Q(hosts=account) | Q(participants=account) | Q(donors=account)
        )
        return cls.objects.filter(
            Q(pk__in=freeform_subs)
            | Q(pk__in=recruitment_subs)
            | Q(pk__in=sotm_subs)
            | Q(pk__in=pvm_split_subs)
            | Q(pk__in=mentor_subs)
            | Q(pk__in=event_subs)
        )

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


class FreeformSubmission(DragonstoneBaseSubmission):
    account = models.ForeignKey(
        "account.Account",
        on_delete=models.CASCADE,
        related_name="freeform_dragonstone_pts",
    )
    created_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    dragonstone_pts = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "Freeform Dragonstone Points (Staff Only)"
        verbose_name_plural = "Freeform Dragonstone Points (Staff Only)"

    @classmethod
    def annotate_dragonstone_pts(cls, account=None):
        """
        Return a list containing (account, dragonstone_pts) values.
        If account is provided, return only the dragonstone points for that account.
        Only consider submission made within the last 3 months.
        """
        dragonstone_pts = cls.objects.accepted().filter(date__gte=expiration_period)
        if account:
            return (
                dragonstone_pts.filter(account=account).aggregate(
                    total_dragonstone_pts=Sum("dragonstone_pts")
                )["total_dragonstone_pts"]
                or 0
            )
        return list(dragonstone_pts.values("account", "dragonstone_pts"))

    def type_display(self):
        return "Freeform Submission"

    def value_display(self):
        return f"{self.account} was given {self.dragonstone_pts} points by {self.created_by}"


class RecruitmentSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = "dragonstone/recruitment/proof/"

    recruiter = models.ForeignKey(
        "account.Account", on_delete=models.CASCADE, related_name="recruited"
    )
    recruited = models.ForeignKey(
        "account.Account", on_delete=models.CASCADE, related_name="recruited_by"
    )

    class Meta:
        verbose_name = "Recruitment Submission (Staff Only)"
        verbose_name_plural = "Recruitment Submissions (Staff Only)"

    @classmethod
    def annotate_dragonstone_pts(cls, account=None):
        """
        Return a list containing (account, dragonstone_pts) values.
        If account is provided, return only the dragonstone points for that account.
        Only consider submission made within the last 3 months.
        """
        dragonstone_pts = (
            cls.objects.accepted()
            .filter(date__gte=expiration_period)
            .annotate(
                dragonstone_pts=Value(
                    int(Settings.objects.get(name="RECRUITER_PTS").value)
                ),
                account=F("recruiter"),
            )
        )
        if account:
            return (
                dragonstone_pts.filter(recruiter=account).aggregate(
                    total_dragonstone_pts=Sum("dragonstone_pts")
                )["total_dragonstone_pts"]
                or 0
            )
        return list(dragonstone_pts.values("account", "dragonstone_pts"))

    def type_display(self):
        return "Recruitment Submission"

    def value_display(self):
        return f"{self.recruiter} recruited {self.recruited}"


class SotMSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = "dragonstone/sotm/proof/"

    account = models.ForeignKey("account.Account", on_delete=models.CASCADE)
    rank = models.PositiveIntegerField(choices=((1, "1st"), (2, "2nd"), (3, "3rd")))

    class Meta:
        verbose_name = "Skill of the Month Submission (Staff Only)"
        verbose_name_plural = "Skill of the Month Submissions (Staff Only)"

    @classmethod
    def annotate_dragonstone_pts(cls, account=None):
        """
        Return a list containing (account, dragonstone_pts) values.
        Only consider submission made within the last 3 months.
        """
        dragonstone_pts = (
            cls.objects.accepted()
            .filter(date__gte=expiration_period)
            .annotate(
                dragonstone_pts=Case(
                    When(
                        rank=1,
                        then=int(Settings.objects.get(name="SOTM_FIRST_PTS").value),
                    ),
                    When(
                        rank=2,
                        then=int(Settings.objects.get(name="SOTM_SECOND_PTS").value),
                    ),
                    When(
                        rank=3,
                        then=int(Settings.objects.get(name="SOTM_THIRD_PTS").value),
                    ),
                    default=Value(0),
                )
            )
        )
        if account:
            return (
                dragonstone_pts.filter(account=account).aggregate(
                    total_dragonstone_pts=Sum("dragonstone_pts")
                )["total_dragonstone_pts"]
                or 0
            )
        return list(dragonstone_pts.values("account", "dragonstone_pts"))

    def type_display(self):
        return "Skill of the Month Submission"

    def value_display(self):
        return f"{self.account.name} - {self.get_rank_display()}"


class PVMSplitSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = "dragonstone/pvm/proof/"

    accounts = models.ManyToManyField("account.Account")
    content = models.ForeignKey("main.Content", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "PVM Split Submission"
        verbose_name_plural = "PVM Split Submissions"

    @classmethod
    def annotate_dragonstone_pts(cls, account=None):
        """
        Return a list containing (account, dragonstone_pts) values.
        Only consider submission made within the last 3 months.
        """
        dragonstone_qs = (
            cls.objects.accepted()
            .filter(date__gte=expiration_period)
            .annotate(
                dragonstone_pts=Case(
                    When(
                        content__difficulty=EASY,
                        then=int(
                            Settings.objects.get(name="PVM_SPLITS_EASY_PTS").value
                        ),
                    ),
                    When(
                        content__difficulty=MEDIUM,
                        then=int(
                            Settings.objects.get(name="PVM_SPLITS_MEDIUM_PTS").value
                        ),
                    ),
                    When(
                        content__difficulty=HARD,
                        then=int(
                            Settings.objects.get(name="PVM_SPLITS_HARD_PTS").value
                        ),
                    ),
                    When(
                        content__difficulty=VERY_HARD,
                        then=int(
                            Settings.objects.get(name="PVM_SPLITS_VERY_HARD_PTS").value
                        ),
                    ),
                    default=Value(0),
                ),
                account=F("accounts"),
            )
        )
        if account:
            dragonsone_qs = (
                dragonstone_qs.values("accounts")
                .order_by("accounts")
                .annotate(total_dragonstone_pts=Sum("dragonstone_pts"))
                .filter(account=account.id)
                .first()
            )
            if dragonsone_qs:
                return dragonsone_qs["total_dragonstone_pts"]
            return 0
        return list(dragonstone_qs.values("account", "dragonstone_pts"))

    def type_display(self):
        return "PVM Split Submission"

    def value_display(self):
        return f'{", ".join(self.accounts.values_list("name", flat=True))} - {self.content.name}'


class MentorSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = "dragonstone/mentor/proof/"

    mentors = models.ManyToManyField("account.Account", related_name="mentored")
    learners = models.ManyToManyField("account.Account", related_name="mentor_learners")
    content = models.ForeignKey("main.Content", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Mentor Submission"
        verbose_name_plural = "Mentor Submissions"

    @classmethod
    def annotate_dragonstone_pts(cls, account=None):
        """
        Return a list containing (account, dragonstone_pts) values.
        Only consider submission made within the last 3 months.
        """
        dragonsone_qs = (
            cls.objects.accepted()
            .filter(date__gte=expiration_period)
            .annotate(
                dragonstone_pts=Case(
                    When(
                        content__difficulty=EASY,
                        then=int(Settings.objects.get(name="MENTOR_EASY_PTS").value),
                    ),
                    When(
                        content__difficulty=MEDIUM,
                        then=int(Settings.objects.get(name="MENTOR_MEDIUM_PTS").value),
                    ),
                    When(
                        content__difficulty=HARD,
                        then=int(Settings.objects.get(name="MENTOR_HARD_PTS").value),
                    ),
                    When(
                        content__difficulty=VERY_HARD,
                        then=int(
                            Settings.objects.get(name="MENTOR_VERY_HARD_PTS").value
                        ),
                    ),
                    default=Value(0),
                ),
                account=F("mentors"),
            )
        )
        if account:
            dragonsone_qs = (
                dragonsone_qs.values("mentors")
                .order_by("mentors")
                .annotate(total_dragonstone_pts=Sum("dragonstone_pts"))
                .filter(account=account.id)
                .first()
            )
            if dragonsone_qs:
                return dragonsone_qs["total_dragonstone_pts"]
            return 0
        return list(dragonsone_qs.values("account", "dragonstone_pts"))

    def type_display(self):
        return "Mentor Submission"

    def value_display(self):
        return f'Mentorship by {", ".join(self.mentors.values_list("name", flat=True))} for {self.content.name}'


class EventSubmission(DragonstoneBaseSubmission):
    UPLOAD_TO = "dragonstone/event/proof/"

    name = models.CharField(max_length=256)
    hosts = models.ManyToManyField(
        "account.Account", related_name="events_hosted", blank=True
    )
    participants = models.ManyToManyField(
        "account.Account", related_name="events_participated", blank=True
    )
    donors = models.ManyToManyField(
        "account.Account", related_name="events_donated", blank=True
    )
    type = models.IntegerField(choices=EVENT_CHOICES)

    class Meta:
        verbose_name = "Event Submission"
        verbose_name_plural = "Event Submissions"

    @classmethod
    def annotate_dragonstone_pts(cls, account=None):
        """
        Return a list containing (account, dragonstone_pts) values.
        Only consider submission made within the last 3 months.
        """
        hosts_qs = (
            cls.objects.accepted()
            .filter(date__gte=expiration_period)
            .annotate(
                dragonstone_pts=Case(
                    When(
                        Q(type=PVM) | Q(type=SKILLING),
                        then=int(
                            Settings.objects.get(name="EVENT_MINOR_HOSTS_PTS").value
                        ),
                    ),
                    When(
                        type=EVENT_MENTOR,
                        then=int(
                            Settings.objects.get(name="EVENT_MENTOR_HOSTS_PTS").value
                        ),
                    ),
                    When(
                        type=MAJOR,
                        then=int(
                            Settings.objects.get(name="EVENT_MAJOR_HOSTS_PTS").value
                        ),
                    ),
                    When(
                        type=OTHER,
                        then=int(
                            Settings.objects.get(name="EVENT_OTHER_HOSTS_PTS").value
                        ),
                    ),
                    default=Value(0),
                ),
                account=F("hosts"),
            )
        )

        participants_qs = (
            cls.objects.accepted()
            .filter(date__gte=expiration_period)
            .annotate(
                dragonstone_pts=Case(
                    When(
                        Q(type=PVM) | Q(type=SKILLING),
                        then=int(
                            Settings.objects.get(
                                name="EVENT_MINOR_PARTICIPANTS_PTS"
                            ).value
                        ),
                    ),
                    When(
                        type=EVENT_MENTOR,
                        then=int(
                            Settings.objects.get(
                                name="EVENT_MENTOR_PARTICIPANTS_PTS"
                            ).value
                        ),
                    ),
                    When(
                        type=MAJOR,
                        then=int(
                            Settings.objects.get(
                                name="EVENT_MAJOR_PARTICIPANTS_PTS"
                            ).value
                        ),
                    ),
                    When(
                        type=OTHER,
                        then=int(
                            Settings.objects.get(
                                name="EVENT_OTHER_PARTICIPANTS_PTS"
                            ).value
                        ),
                    ),
                    default=Value(0),
                ),
                account=F("participants"),
            )
        )

        donors_qs = (
            cls.objects.accepted()
            .filter(date__gte=expiration_period)
            .annotate(
                dragonstone_pts=Case(
                    When(
                        Q(type=PVM) | Q(type=SKILLING),
                        then=int(
                            Settings.objects.get(name="EVENT_MINOR_DONORS_PTS").value
                        ),
                    ),
                    When(
                        type=EVENT_MENTOR,
                        then=int(
                            Settings.objects.get(name="EVENT_MENTOR_DONORS_PTS").value
                        ),
                    ),
                    When(
                        type=MAJOR,
                        then=int(
                            Settings.objects.get(name="EVENT_MAJOR_DONORS_PTS").value
                        ),
                    ),
                    When(
                        type=OTHER,
                        then=int(
                            Settings.objects.get(name="EVENT_OTHER_DONORS_PTS").value
                        ),
                    ),
                    default=Value(0),
                ),
                account=F("donors"),
            )
        )

        if account:
            hosts_qs = (
                hosts_qs.values("hosts")
                .order_by("hosts")
                .annotate(total_dragonstone_pts=Sum("dragonstone_pts"))
                .filter(account=account.id)
                .first()
            )
            hosts_pts = hosts_qs["total_dragonstone_pts"] if hosts_qs else 0

            participants_qs = (
                participants_qs.values("participants")
                .order_by("participants")
                .annotate(total_dragonstone_pts=Sum("dragonstone_pts"))
                .filter(account=account.id)
                .first()
            )
            participants_pts = (
                participants_qs["total_dragonstone_pts"] if participants_qs else 0
            )

            donors_qs = (
                donors_qs.values("donors")
                .order_by("donors")
                .annotate(total_dragonstone_pts=Sum("dragonstone_pts"))
                .filter(account=account.id)
                .first()
            )
            donors_pts = donors_qs["total_dragonstone_pts"] if donors_qs else 0
        else:
            hosts_pts = list(hosts_qs.values("account", "dragonstone_pts"))
            participants_pts = list(
                participants_qs.values("account", "dragonstone_pts")
            )
            donors_pts = list(donors_qs.values("account", "dragonstone_pts"))

        return hosts_pts + participants_pts + donors_pts

    def type_display(self):
        return "Event Submission"

    def value_display(self):
        return f"{self.name}"
