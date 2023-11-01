from django.db import migrations

EASY, MEDIUM, HARD, VERY_HARD = range(4)
PVM, SKILLING, MAJOR, OTHER, EVENT_MENTOR = range(5)


def forward(apps, schema_data):
    log_entry_model = apps.get_model("admin", "LogEntry")
    content_type_model = apps.get_model("contenttypes", "ContentType")

    # points models
    dragonstone_points_model = apps.get_model("dragonstone", "DragonstonePoints")
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

    # submission models
    freeform_submission_model = apps.get_model("dragonstone", "FreeformSubmission")
    recruitment_submission_model = apps.get_model(
        "dragonstone", "RecruitmentSubmission"
    )
    sotm_submission_model = apps.get_model("dragonstone", "SotMSubmission")
    pvm_split_submission_model = apps.get_model("dragonstone", "PVMSplitSubmission")
    mentor_submission_model = apps.get_model("dragonstone", "MentorSubmission")
    event_submission_model = apps.get_model("dragonstone", "EventSubmission")

    for submission in freeform_submission_model.objects.all():
        freeform_points_model.objects.create(
            account=submission.account,
            points=submission.dragonstone_pts,
            date=submission.date,
            created_by=submission.created_by,
        )

    for submission in recruitment_submission_model.objects.all():
        recruitment_points_model.objects.create(
            account=submission.recruiter,
            points=2,
            date=submission.date,
            recruited=submission.recruited,
        )

    for submission in sotm_submission_model.objects.all():
        if submission.rank == 1:
            points = 3
        elif submission.rank == 2:
            points = 2
        else:
            points = 1
        sotm_points_model.objects.create(
            account=submission.account,
            points=points,
            date=submission.date,
            rank=submission.rank,
        )

    for submission in pvm_split_submission_model.objects.all():
        if submission.content.difficulty == EASY:
            points = 0
        elif (
            submission.content.difficulty == MEDIUM
            or submission.content.difficulty == HARD
        ):
            points = 1
        else:
            points = 2

        for account in submission.accounts.all():
            pvm_split_points_model.objects.create(
                account=account,
                submission=submission,
                points=points,
                date=submission.date,
            )

    for submission in mentor_submission_model.objects.all():
        if submission.content.difficulty == EASY:
            points = 1
        elif submission.content.difficulty == MEDIUM:
            points = 2
        elif submission.content.difficulty == HARD:
            points = 3
        else:
            points = 4

        for mentor in submission.mentors.all():
            mentor_points_model.objects.create(
                account=mentor,
                submission=submission,
                points=points,
                date=submission.date,
            )

    for submission in event_submission_model.objects.all():
        points_dict = {
            OTHER: {
                "host": 3,
                "participant": 1,
                "donor": 0,
            },
            MAJOR: {
                "host": 15,
                "participant": 5,
                "donor": 2,
            },
            EVENT_MENTOR: {
                "host": 5,
                "participant": 2,
                "donor": 0,
            },
            PVM: {
                "host": 5,
                "participant": 2,
                "donor": 0,
            },
            SKILLING: {
                "host": 5,
                "participant": 2,
                "donor": 0,
            },
        }
        for host in submission.hosts.all():
            event_host_points_model.objects.create(
                account=host,
                submission=submission,
                points=points_dict[submission.type]["host"],
                date=submission.date,
            )
        for participant in submission.participants.all():
            event_participant_points_model.objects.create(
                account=participant,
                submission=submission,
                points=points_dict[submission.type]["participant"],
                date=submission.date,
            )
        for donor in submission.donors.all():
            event_donor_points_model.objects.create(
                account=donor,
                submission=submission,
                points=points_dict[submission.type]["donor"],
                date=submission.date,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("dragonstone", "0013_dragonstonepoints_and_more"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
