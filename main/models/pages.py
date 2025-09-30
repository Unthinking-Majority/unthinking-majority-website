from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.search import index

from main import THEME_CHOICES
from main.blocks import BannerBlock, EmojiRowBlock, EmbedBlock

__all__ = [
    "HomePage",
    "ContentPage",
]


class HomePage(Page):
    """
    Home page model.
    Only one home page is allowed.
    """

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]

    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Upload an image/gif to display on the home page of the website.",
    )

    body = StreamField(
        [
            ("banner", BannerBlock()),
        ],
        null=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("logo"),
        FieldPanel("body"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]


class ContentPage(Page):
    """
    Generic content page model for creating various kinds of pages, such as the pvm resources pages.
    """

    author = models.CharField(
        max_length=64,
        blank=True,
        help_text="Leave blank to automatically show authors as all users who have edited this page.",
    )
    theme = models.CharField(choices=THEME_CHOICES)
    show_page_index = models.BooleanField(default=False)
    body = StreamField(
        [
            ("heading_2", blocks.CharBlock(max_length=128)),
            ("heading_3", blocks.CharBlock(max_length=128)),
            (
                "rich_text",
                blocks.RichTextBlock(
                    features=[
                        "bold",
                        "italic",
                        "ol",
                        "ul",
                        "document link",
                        "link",
                    ]
                ),
            ),
            ("image", ImageChooserBlock()),
            ("embed", EmbedBlock()),
            ("emoji_row", EmojiRowBlock()),
        ],
    )

    content_panels = Page.content_panels + [
        FieldPanel("author"),
        FieldPanel("theme"),
        FieldPanel("show_page_index"),
        FieldPanel("body"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]
