from django.db import migrations


def forwards(apps, schema_data):
    board_model = apps.get_model('main', 'Board')
    parent_board_model = apps.get_model('main', 'ParentBoard')

    for board in board_model.objects.all():
        parent_board = parent_board_model.objects.create(
            name=board.name,
            category=board.category,
            metric=board.metric,
            metric_name=board.metric_name,
            icon=board.icon
        )
        board.parent = parent_board
        board.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_board_parent_20230112_0423'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop)
    ]
