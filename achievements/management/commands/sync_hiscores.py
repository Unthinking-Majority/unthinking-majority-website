import asyncio

import aiohttp
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from account.models import Account
from achievements.models import Hiscores
from main import SKILLS
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
        skills = [
            "Overall",
            *[i[1] for i in SKILLS],
        ]  # 23 skills + overall section at top

        activities = [
            "League Points",
            "Deadman Points",
            "Bounty Hunter - Hunter",
            "Bounty Hunter - Rogue",
            "Bounty Hunter(Legacy) - Hunter",
            "Bounty Hunter(Legacy) - Rogue",
            "Clue Scrolls(all)",
            "Clue Scrolls(beginner)",
            "Clue Scrolls(easy)",
            "Clue Scrolls(medium)",
            "Clue Scrolls(hard)",
            "Clue Scrolls(elite)",
            "Clue Scrolls(master)",
            "LMS - Rank",
            "PvP Arena - Rank",
            "Soul Wars Zeal",
            "Rifts closed",
        ]  # 17 activities

        # Why the shit did Jagex do alphabetical order for all of these except PNM??? Makes my life harder!!!
        bosses = [
            "Colosseum Glory",
            "Abyssal Sire",
            "Alchemical Hydra",
            "Amoxliatl",
            "Araxxor",
            "Artio",
            "Barrows Chests",
            "Bryophyta",
            "Callisto",
            "Calvar'ion",
            "Cerberus",
            "Chambers of Xeric",
            "Chambers of Xeric: Challenge Mode",
            "Chaos Elemental",
            "Chaos Fanatic",
            "Commander Zilyana",
            "Corporeal Beast",
            "Crazy Archaeologist",
            "Dagannoth Prime",
            "Dagannoth Rex",
            "Dagannoth Supreme",
            "Deranged Archaeologist",
            "Duke Sucellus",
            "General Graardor",
            "Giant Mole",
            "Grotesque Guardians",
            "Hespori",
            "Kalphite Queen",
            "King Black Dragon",
            "Kraken",
            "Kree'Arra",
            "K'ril Tsutsaroth",
            "Lunar Chests",
            "Mimic",
            "Nex",
            "Nightmare",
            "Phosani's Nightmare",
            "Obor",
            "Phantom Muspah",
            "Sarachnis",
            "Scorpia",
            "Scurrius",
            "Skotizo",
            "Sol Heredit",
            "Spindel",
            "Tempoross",
            "The Gauntlet",
            "The Corrupted Gauntlet",
            "The Hueycoatl",
            "The Leviathan",
            "The Royal Titans",
            "The Whisperer",
            "Theatre of Blood",
            "Theatre of Blood: Hard Mode",
            "Thermonuclear Smoke Devil",
            "Tombs of Amascut",
            "Tombs of Amascut: Expert Mode",
            "TzKal-Zuk",
            "TzTok-Jad",
            "Vardorvis",
            "Venenatis",
            "Vet'ion",
            "Vorkath",
            "Wintertodt",
            "Zalcano",
            "Zulrah",
        ]  # 60 hiscores (59 bosses + glory for colosseum!)

        results = asyncio.run(
            main(
                list(
                    Account.objects.filter(is_active=True).values_list(
                        "name", flat=True
                    )
                ),
            )
        )

        data = []
        for username, result in results:
            if not result:
                continue
            hiscores_data = []
            for line in result.split("\n"):
                hiscores_data.append(line.split(","))
            data.append(
                (username, zip(bosses, hiscores_data[len(skills) + len(activities) :]))
            )
        objs = []
        for username, result in data:
            for hiscores_name, hiscore in result:
                try:
                    rank, kc = hiscore
                except ValueError:
                    raise CommandError(
                        f"ValueError: Not enough values to unpack. Account: {username} {hiscores_name} values:{hiscore}"
                    )

                try:
                    content = Content.objects.get(hiscores_name__iexact=hiscores_name)
                except Content.DoesNotExist:
                    raise CommandError(
                        f"No Content object exists with hiscores_name={hiscores_name}"
                    )

                account = Account.objects.get(name=username)

                objs.append(
                    Hiscores(
                        account=account,
                        content=content,
                        score=kc,
                        rank_overall=rank,
                    )
                )

        Hiscores.objects.bulk_create(
            objs,
            update_conflicts=True,
            unique_fields=["account", "content"],
            update_fields=["score", "rank_overall"],
        )
