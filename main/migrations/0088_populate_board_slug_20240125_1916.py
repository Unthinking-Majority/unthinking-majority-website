from django.db import migrations
from django.utils.text import slugify


def forward(apps, schema_data):
    board_model = apps.get_model("main", "Board")
    for board in board_model.objects.all():
        board.slug = slugify(board.name)
        board.save()


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0087_board_slug"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
