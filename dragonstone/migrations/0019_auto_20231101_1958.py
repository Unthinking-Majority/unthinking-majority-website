from django.db import migrations


def forward(apps, schema_data):
    freeform_points_model = apps.get_model("dragonstone", "FreeformPoints")
    recruitment_points_model = apps.get_model("dragonstone", "RecruitmentPoints")
    sotm_points_model = apps.get_model("dragonstone", "SotMPoints")
    pvm_split_points_model = apps.get_model("dragonstone", "PVMSplitPoints")
    mentor_points_model = apps.get_model("dragonstone", "MentorPoints")
    event_host_points_model = apps.get_model("dragonstone", "EventHostPoints")
    event_participant_points_model = apps.get_model(
        "dragonstone", "EventParticipantPoints"
    )
    event_donor_points_model = apps.get_model("dragonstone", "EventDonorPoints")

    content_type_model = apps.get_model("contenttypes", "ContentType")

    freeform_points_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            freeform_points_model
        )
    )
    recruitment_points_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            recruitment_points_model
        )
    )
    sotm_points_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(sotm_points_model)
    )
    pvm_split_points_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            pvm_split_points_model
        )
    )
    mentor_points_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            mentor_points_model
        )
    )
    event_host_points_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            event_host_points_model
        )
    )
    event_participant_points_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            event_participant_points_model
        )
    )
    event_donor_points_model.objects.update(
        polymorphic_ctype_id=content_type_model.objects.get_for_model(
            event_donor_points_model
        )
    )


class Migration(migrations.Migration):
    dependencies = [
        ("dragonstone", "0018_alter_eventdonorpoints_options_and_more"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
