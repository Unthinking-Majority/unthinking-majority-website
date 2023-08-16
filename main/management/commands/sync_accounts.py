import asyncio

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from wom import Client

from account.models import Account

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
        account_names = [
            name.lower()
            for name in Account.objects.all().values_list("name", flat=True)
        ]

        loop = asyncio.get_event_loop()

        # start client
        loop.run_until_complete(client.start())

        memberships = loop.run_until_complete(get_memberships())

        for membership in memberships:
            if membership.player.display_name.lower() not in account_names:
                name_changes = loop.run_until_complete(
                    get_name_changes(membership.player.display_name)
                )
                old_accounts = Account.objects.filter(
                    name__in=[obj.old_name for obj in name_changes]
                )

                if old_accounts.exists():
                    print(
                        old_accounts.count(),
                        old_accounts,
                        membership.player.display_name,
                    )
                else:
                    print(f"doesnt exist: {membership.player.display_name}")

        # close client
        loop.run_until_complete(client.close())

        # account_names = accounts.values_list("name", flat=True)
        # print(member.player.display_name, member.membership.role)
        # asyncio.run(sync_accounts())
