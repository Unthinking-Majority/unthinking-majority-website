from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0030_parentboard"),
    ]

    operations = [
        migrations.AddField(
            model_name="board",
            name="parent",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="boards",
                to="main.parentboard",
                null=True,
            ),
            preserve_default=False,
        ),
    ]
