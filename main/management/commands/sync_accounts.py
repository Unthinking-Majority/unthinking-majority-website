import asyncio

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from wom import Client

from account import WOM_ROLE_MAPPINGS
from account.models import Account
from main.models import UMNotification

client = Client()
client.set_api_key(settings.WOM_API_KEY)


async def get_memberships():
    result = await client.groups.get_details(44)

    if result.is_ok:
        members = result.unwrap().memberships
    else:
        members = None
        print(f"Error: {result.unwrap_err()}")

    return members


async def get_name_changes(username):
    result = await client.players.get_name_changes(username)

    if result.is_ok:
        name_changes = result.unwrap()
    else:
        name_changes = None
        print(f"Error: {result.unwrap_err()}")

    return name_changes


class Command(BaseCommand):
    help = "Sync current members in clan (+ their ranks) using wise old mands api."

    def handle(self, *args, **options):
        king_of_jelly = User.objects.get(username="stinky")

        accounts = Account.objects.all()
        account_names = [
            name.lower() for name in accounts.values_list("name", flat=True)
        ]

        # notification_recipients = User.objects.filter(
        #     Q(groups=Group.objects.get(name="Administrator")) | Q(is_superuser=True)
        # )
        notification_recipients = User.objects.filter(id=king_of_jelly.id)

        loop = asyncio.get_event_loop()

        # start client
        loop.run_until_complete(client.start())

        memberships = loop.run_until_complete(get_memberships())

        for membership in memberships:
            # get rank
            try:
                rank = WOM_ROLE_MAPPINGS[membership.membership.role]
            except KeyError:
                rank = None

            if membership.player.display_name.lower() not in account_names:
                name_changes = loop.run_until_complete(
                    get_name_changes(membership.player.display_name)
                )
                old_accounts = accounts.filter(
                    name__in=[obj.old_name for obj in name_changes]
                )

                if old_accounts.exists():
                    # player has changed their name, must update account name
                    if old_accounts.count() > 1:
                        raise CommandError(
                            f"More than one account found which matches an old name for {membership.player.display_name}"
                        )

                    account = old_accounts.first()
                    old_name = account.name
                    account.name = membership.player.display_name
                    for recipient in notification_recipients:
                        UMNotification.objects.create(
                            actor_object_id=king_of_jelly.account.id,
                            actor_content_type=ContentType.objects.get_for_model(
                                king_of_jelly.account
                            ),
                            verb=f"updated name for {old_name} to",
                            recipient=recipient,
                            action_object_object_id=account.id,
                            action_object_content_type=ContentType.objects.get_for_model(
                                account
                            ),
                        )
                    print(f"updated {old_name} to {membership.player.display_name}")
                else:
                    # player was never added, must create new account object
                    account = Account.objects.create(
                        name=membership.player.display_name,
                    )
                    for recipient in notification_recipients:
                        UMNotification.objects.create(
                            actor_object_id=king_of_jelly.account.id,
                            actor_content_type=ContentType.objects.get_for_model(
                                king_of_jelly.account
                            ),
                            verb=f"created new account",
                            recipient=recipient,
                            action_object_object_id=account.id,
                            action_object_content_type=ContentType.objects.get_for_model(
                                account
                            ),
                        )
                    print(f"created {account}")
            else:
                # player has account already
                account = accounts.get(
                    name__iexact=membership.player.display_name.lower()
                )

            if rank:
                account.rank = rank
                for recipient in notification_recipients:
                    UMNotification.objects.create(
                        actor_object_id=king_of_jelly.account.id,
                        actor_content_type=ContentType.objects.get_for_model(
                            king_of_jelly.account
                        ),
                        verb=f"updated rank for",
                        recipient=recipient,
                        action_object_object_id=account.id,
                        action_object_content_type=ContentType.objects.get_for_model(
                            account
                        ),
                    )
                print(f"updated rank for {account} to {rank}")

            account.save()

        # close client
        loop.run_until_complete(client.close())

        # print(member.player.display_name, member.membership.role)
