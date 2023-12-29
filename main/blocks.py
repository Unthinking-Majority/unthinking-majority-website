from wagtail import blocks

from main import THEME_CHOICES


class BannerBlock(blocks.StructBlock):
    theme = blocks.ChoiceBlock(choices=THEME_CHOICES)
    title = blocks.RichTextBlock(
        features=[
            "image",
        ]
    )
    description = blocks.TextBlock()
    link = blocks.PageChooserBlock()

    class Meta:
        icon = "pick"
        template = "main/blocks/banner_block.html"
