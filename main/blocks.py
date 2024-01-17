from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

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


class EmojiRowBlock(blocks.StructBlock):
    emoji = ImageChooserBlock()
    text = blocks.TextBlock()

    class Meta:
        icon = "pick"
        template = "main/blocks/emoji_row_block.html"
