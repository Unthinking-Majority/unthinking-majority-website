from django.db import migrations


def forward(apps, schema_data):
    board_model = apps.get_model("main", "Board")
    for board in board_model.objects.all():
        board.metric = board.content.metric
        board.metric_name = board.content.metric_name
        board.save()
        print(f"Updated {board} with {board.metric} and {board.metric_name}")


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0107_board_metric_board_metric_name"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
