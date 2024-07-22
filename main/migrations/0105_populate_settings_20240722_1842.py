from django.db import migrations


def forward(apps, schema_data):
    settings_model = apps.get_model("main", "Settings")
    constance_model = apps.get_model("constance", "Constance")
    for obj in constance_model.objects.all():
        setting = settings_model.objects.create(key=obj.key, value=obj.value)


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0104_settings"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
