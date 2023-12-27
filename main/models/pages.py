from django.db import models

from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.search import index

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

    content_panels = [FieldPanel("logo")]


class ContentPage(Page):
    """
    Generic content page model for creating various kinds of pages, such as the pvm resources pages.
    """

    THEME_CHOICES = (
        ("teal", "Teal"),
        ("purple", "Purple"),
        ("brown", "Brown"),
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
            ("embed", EmbedBlock(max_width=960, max_height=540)),
        ],
        use_json_field=True,
    )

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("theme"),
        FieldPanel("show_page_index"),
        FieldPanel("body"),
    ]
