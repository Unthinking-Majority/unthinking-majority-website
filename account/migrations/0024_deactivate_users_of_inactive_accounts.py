from django.db import migrations


def deactivate_users_of_inactive_accounts(apps, schema_editor):
    User = apps.get_model("auth", "User")
    User.objects.filter(
        account__is_active=False, is_active=True, is_staff=False, is_superuser=False
    ).update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0023_hash_usercreationsubmission_passwords"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(
            deactivate_users_of_inactive_accounts, migrations.RunPython.noop
        ),
    ]
