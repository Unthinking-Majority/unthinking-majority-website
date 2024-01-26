from django.db import migrations


def forward(apps, schema_data):
    content_model = apps.get_model("main", "Content")
    for content in content_model.objects.all():
        content.hiscores_name = content.name
        content.save()
        print(f"Updated hiscores name for {content.name} to {content.hiscores_name}")


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0092_content_hiscores_name_alter_content_name"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
