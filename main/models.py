from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils.html import format_html
from notifications.models import Notification

from main import DIFFICULTY_CHOICES, EASY, METRIC_CHOICES, TIME
from um.functions import get_file_path


class Board(models.Model):
    name = models.CharField(max_length=256, unique=True)
    content = models.ForeignKey(
        "main.Content", on_delete=models.CASCADE, related_name="boards"
    )
    team_size = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    flex_order = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Order on leaderboard page. Empty values will appear last (order is then defined by team size). Allowed numbers are 1 - 12.",
    )

    class Meta:
        ordering = ["team_size", "name"]

    def __str__(self):
        return self.name


class Content(models.Model):
    UPLOAD_TO = "board/icons/"

    name = models.CharField(max_length=256, unique=True)
    category = models.ForeignKey(
        "main.ContentCategory", on_delete=models.CASCADE, related_name="content_types"
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
        return self.content_types.filter(is_pb=True)


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


class Settings(models.Model):
    display_name = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    value = models.CharField(max_length=256)

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"
