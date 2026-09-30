from django.db import migrations


def delete_orphaned_dragonstone_submissions(apps, schema_editor):
    """
    Delete pending dragonstone submissions that only exist as a base row, without the row of any submission type.
    """
    ContentType = apps.get_model("contenttypes", "ContentType")
    DragonstoneBaseSubmission = apps.get_model(
        "dragonstone", "DragonstoneBaseSubmission"
    )
    base_ctype = ContentType.objects.filter(
        app_label="dragonstone", model="dragonstonebasesubmission"
    ).first()
    if base_ctype is None:
        return

    orphans = DragonstoneBaseSubmission.objects.filter(
        accepted__isnull=True, polymorphic_ctype=base_ctype
    )
    for model in apps.get_app_config("dragonstone").get_models():
        if any(f.name == "dragonstonebasesubmission_ptr" for f in model._meta.fields):
            orphans = orphans.exclude(
                pk__in=model.objects.values("dragonstonebasesubmission_ptr_id")
            )

    for pk in orphans.values_list("pk", flat=True):
        DragonstoneBaseSubmission.objects.filter(pk=pk).delete()
        print(f"\n  Deleted orphaned dragonstone submission {pk}")


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0114_alter_board_submissions_ordering"),
        ("dragonstone", "0028_alter_sotmpoints_skill"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        # django-constance is no longer installed, but its table and migration records were left behind
        migrations.RunSQL(
            [
                "DROP TABLE IF EXISTS constance_constance",
                "DELETE FROM django_migrations WHERE app = 'constance'",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunPython(
            delete_orphaned_dragonstone_submissions, migrations.RunPython.noop
        ),
    ]
