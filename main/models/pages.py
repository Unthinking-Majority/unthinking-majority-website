from wagtail import blocks
from wagtail.admin.panels import FieldPanel
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
    Empty home page model to transfer current home page to a wagtail system. In the future we can expand on this!
    """

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]


class ContentPage(Page):
    body = StreamField(
        [
            ("heading", blocks.CharBlock(max_length=256)),
            ("rich_text", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        use_json_field=True,
    )

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
