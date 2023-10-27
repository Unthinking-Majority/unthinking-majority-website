from django.db import migrations


def forward(apps, schema_data):
    freeform_submission_model = apps.get_model("dragonstone", "FreeformSubmission")
    recruitment_submission_model = apps.get_model(
        "dragonstone", "RecruitmentSubmission"
    )
    sotm_submission_model = apps.get_model("dragonstone", "SotMSubmission")
    pvm_split_submission_model = apps.get_model("dragonstone", "PVMSplitSubmission")
    mentor_submission_model = apps.get_model("dragonstone", "MentorSubmission")
    event_submission_model = apps.get_model("dragonstone", "EventSubmission")

    content_type_model = apps.get_model("contenttypes", "ContentType")

    freeform_submission_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            freeform_submission_model
        )
    )
    recruitment_submission_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            recruitment_submission_model
        )
    )
    sotm_submission_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            sotm_submission_model
        )
    )
    pvm_split_submission_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            pvm_split_submission_model
        )
    )
    mentor_submission_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            mentor_submission_model
        )
    )
    event_submission_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            event_submission_model
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ("dragonstone", "0011_dragonstonebasesubmission_polymorphic_ctype"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
