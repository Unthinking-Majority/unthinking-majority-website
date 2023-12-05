from wagtail.images.formats import (
    Format,
    register_image_format,
    unregister_image_format,
)

unregister_image_format("right")
unregister_image_format("left")

register_image_format(
    Format("right", "Right", "richtext-image float-right", "scale-100")
)
register_image_format(Format("left", "Left", "richtext-image float-left", "scale-100"))
