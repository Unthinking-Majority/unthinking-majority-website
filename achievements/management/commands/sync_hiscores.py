import asyncio
import json

import aiohttp
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from account.models import Account
from achievements.models import Hiscores
from main.models import Content


def get_url(username):
    return f"{settings.OSRS_PLAYER_HISCORES_API}{username}"


async def get(session, username):
    url = get_url(username)
    async with session.get(url) as response:
        if response.status != 200:
            print(username, response.status)
            return username, None
        return username, await response.text()


async def main(usernames):
    conn = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=conn) as session:
        return await asyncio.gather(*[get(session, username) for username in usernames])


class Command(BaseCommand):
    help = "Syncs active users hiscores for all content using the official OSRS api."

    def handle(self, *args, **options):
        results = asyncio.run(
            main(
                list(
                    Account.objects.filter(is_active=True).values_list(
                        "name", flat=True
                    )
                ),
            )
        )

        objs = []
        for username, result in results:
            if not result:
                continue
            result = json.loads(result)
            for hiscore in result["activities"]:
                try:
                    content = Content.objects.get(hiscores_name__iexact=hiscore["name"])
                except Content.DoesNotExist:
                    continue

                account = Account.objects.get(name=username)

                objs.append(
                    Hiscores(
                        account=account,
                        content=content,
                        score=hiscore["score"],
                        rank_overall=hiscore["rank"],
                    )
                )

        Hiscores.objects.bulk_create(
            objs,
            update_conflicts=True,
            unique_fields=["account", "content"],
            update_fields=["score", "rank_overall"],
        )
