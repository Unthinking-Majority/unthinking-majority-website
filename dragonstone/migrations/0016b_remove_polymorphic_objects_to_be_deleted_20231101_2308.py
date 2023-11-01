from django.db import migrations


def forward(apps, schema_data):
    freeform_submission_model = apps.get_model("dragonstone", "FreeformSubmission")
    recruitment_submission_model = apps.get_model(
        "dragonstone", "RecruitmentSubmission"
    )
    sotm_submission_model = apps.get_model("dragonstone", "SotMSubmission")

    for obj in freeform_submission_model.objects.all():
        obj.delete()
    for obj in recruitment_submission_model.objects.all():
        obj.delete()
    for obj in sotm_submission_model.objects.all():
        obj.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("dragonstone", "0016_rename_temp_donors_eventsubmission_donors_and_more"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
