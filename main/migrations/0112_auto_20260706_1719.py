from django.db import migrations


def forward(apps, schema_data):
    content_model = apps.get_model("main", "Content")

    for content in content_model.objects.all():
        for board in content.boards.all():
            board.submissions_ordering = content.ordering
            board.save()


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0111_board_submissions_ordering"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
