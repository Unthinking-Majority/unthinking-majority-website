from django.db import migrations


def forward(apps, schema_data):
    record_submission_model = apps.get_model("achievements", "RecordSubmission")
    pet_submission_model = apps.get_model("achievements", "PetSubmission")
    col_log_submission_model = apps.get_model("achievements", "ColLogSubmission")
    ca_submission_model = apps.get_model("achievements", "CASubmission")
    content_type_model = apps.get_model("contenttypes", "ContentType")

    record_submission_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            record_submission_model
        )
    )
    pet_submission_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            pet_submission_model
        )
    )
    col_log_submission_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            col_log_submission_model
        )
    )
    ca_submission_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            ca_submission_model
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ("achievements", "0008_basesubmission_polymorphic_ctype"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
