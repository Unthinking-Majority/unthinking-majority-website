import asyncio

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.db.models.functions import Lower
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
    help = "Sync current members in clan (+ their ranks) using wise old mans api."

    def handle(self, *args, **options):
        king_of_jelly = User.objects.get(username="stinky")

        accounts = Account.objects.all()
        account_names = [
            name.lower() for name in accounts.values_list("name", flat=True)
        ]

        notification_recipients = User.objects.filter(
            Q(groups=Group.objects.get(name="Administrator")) | Q(is_superuser=True)
        )

        loop = asyncio.get_event_loop()

        # start client
        loop.run_until_complete(client.start())

        memberships = loop.run_until_complete(get_memberships())

        # set users not on WOM to inactive TODO TODO TODO
        # TODO to get this working, we would need to prob do some more manual review
        # of all the current usernames on the site, since there are sometimes slight
        # discrepancies in the names
        # Plus, we need to make sure we are starting to ignore case everywhere!
        inactive_accounts = Account.objects.annotate(name_lower=Lower("name")).filter(
            ~Q(
                name_lower__in=[
                    membership.player.display_name.lower() for membership in memberships
                ]
            )
        )
        inactive_accounts.update(is_active=False)
        for account in inactive_accounts:
            for recipient in notification_recipients:
                UMNotification.objects.create(
                    actor_object_id=king_of_jelly.account.id,
                    actor_content_type=ContentType.objects.get_for_model(
                        king_of_jelly.account
                    ),
                    verb=f"set account to inactive",
                    recipient=recipient,
                    action_object_object_id=account.id,
                    action_object_content_type=ContentType.objects.get_for_model(
                        account
                    ),
                )

        for membership in memberships:
            # get rank
            try:
                rank = WOM_ROLE_MAPPINGS[str(membership.membership.role)]
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
                            f"More than one account found which matches an old name for {membership.player.display_name}: {', '.join(list(old_accounts.values_list('name', flat=True)))}"
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
            else:
                # player has account already
                account = accounts.get(
                    name__iexact=membership.player.display_name.lower()
                )

            if rank and account.rank != rank:
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

            account.save()

        # close client
        loop.run_until_complete(client.close())
