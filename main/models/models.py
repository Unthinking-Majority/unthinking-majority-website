from django.contrib.postgres.aggregates import StringAgg
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import NoReverseMatch, reverse
from notifications.models import Notification

from main import DIFFICULTY_CHOICES, EASY, METRIC_CHOICES, TIME
from um.functions import get_file_path

__all__ = [
    "Board",
    "Content",
    "ContentCategory",
    "Pet",
    "UMNotification",
]


class Board(models.Model):
    name = models.CharField(max_length=256)
    content = models.ForeignKey(
        "main.Content", on_delete=models.CASCADE, related_name="boards"
    )
    team_size = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    slug = models.SlugField()

    class Meta:
        ordering = ["team_size", "name"]

    def __str__(self):
        if self.content.boards.count() > 1:
            return f"{self.content.name} {self.name}"
        return self.name

    def top_submissions(self):
        # annotate the teams (accounts values) into a string so we can order by unique teams of accounts and value
        annotated_submissions = (
            self.submissions.active()
            .accepted()
            .annotate(
                accounts_str=StringAgg(
                    "accounts__name", delimiter=",", ordering="accounts__name"
                )
            )
            .order_by("accounts_str", f"{self.content.ordering}value")
        )

        # grab the first submission for each team (which is the best, since we ordered by value above)
        submissions = {}
        for submission in annotated_submissions:
            if submission.accounts_str not in submissions.keys():
                submissions[submission.accounts_str] = submission.id

        # grab the top 3 submissions (1st, 2nd, 3rd)
        submissions = self.submissions.filter(id__in=submissions.values()).order_by(
            f"{self.content.ordering}value", "date"
        )
        return submissions


class Content(models.Model):
    UPLOAD_TO = "board/icons/"

    name = models.CharField(
        max_length=256,
        unique=True,
        help_text="Display name for this content on the website.",
    )
    hiscores_name = models.CharField(
        max_length=256,
        blank=True,
        help_text="The name of this content on the official OSRS Hiscores page. Must match exactly what is on the hiscores page, case insensitive.",
    )
    has_hiscores = models.BooleanField(
        default=True,
        verbose_name="Check if this content has a corresponding page on the official OSRS hiscores page.",
    )
    category = models.ForeignKey(
        "main.ContentCategory", on_delete=models.CASCADE, related_name="contents"
    )
    difficulty = models.PositiveIntegerField(choices=DIFFICULTY_CHOICES, default=EASY)
    is_pb = models.BooleanField(
        default=False, verbose_name="Display on PB Leaderboards?"
    )
    can_be_mentored = models.BooleanField(
        default=False, verbose_name="Can this content be mentored?"
    )
    can_be_split = models.BooleanField(
        default=False, verbose_name="Can teams split drops from this content?"
    )
    metric = models.IntegerField(choices=METRIC_CHOICES, default=TIME)
    metric_name = models.CharField(max_length=128, default="Time")
    slug = models.SlugField(unique=True)
    icon = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    ordering = models.CharField(
        choices=(("-", "Descending"), ("", "Ascending")),
        default="",
        max_length=1,
        blank=True,
        help_text="Order of values when showing submission from child boards.",
    )
    order = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Order in navbar. Empty values will appear last (order is then defined by alphabetical order of name). Allowed numbers are 1 - 12.",
    )

    class Meta:
        verbose_name = "Content"
        verbose_name_plural = "Content"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def leaderboard_url(self):
        return reverse(
            "leaderboard",
            kwargs={"content_category": self.category.slug, "content_name": self.slug},
        )


class ContentCategory(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Content Category"
        verbose_name_plural = "Content Categories"

    def __str__(self):
        return self.name

    def pb_content(self):
        return self.contents.filter(is_pb=True)


class Pet(models.Model):
    UPLOAD_TO = "pet/icons/"

    name = models.CharField(max_length=256, unique=True)
    icon = models.ImageField(upload_to=get_file_path, null=True, blank=True)

    def __str__(self):
        return self.name


class UMNotification(Notification):
    custom_url = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ("-timestamp",)
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def action_object_url(self):
        try:
            url = reverse(
                "admin:{0}_{1}_change".format(
                    self.action_object_content_type.app_label,
                    self.action_object_content_type.model,
                ),
                args=(self.action_object_object_id,),
            )
            return url
        except NoReverseMatch:
            return self.action_object_object_id
