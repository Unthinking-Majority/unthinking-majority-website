import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from account.models import Account
from achievements.models import Hiscores
from main.models import Content


class Command(BaseCommand):
    help = "Syncs active users kill counts for all content using the official osrs api."

    def handle(self, *args, **options):
        skills = [
            "Overall",
            "Attack",
            "Defence",
            "Strength",
            "Hitpoints",
            "Ranged",
            "Prayer",
            "Magic",
            "Cooking",
            "Woodcutting",
            "Fletching",
            "Fishing",
            "Firemaking",
            "Crafting",
            "Smithing",
            "Mining",
            "Herblore",
            "Agility",
            "Thieving",
            "Slayer",
            "Farming",
            "Runecrafting",
            "Hunter",
            "Construction",
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
        ]  # 17 activites

        # Why the shit did Jagex do alphabetical order for all of these except PNM??? Makes my life harder!!!
        bosses = [
            "Abyssal Sire",
            "Alchemical Hydra",
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
            "Mimic",
            "Nex",
            "Nightmare",
            "Phosani's Nightmare",
            "Obor",
            "Phantom Muspah",
            "Sarachnis",
            "Scorpia",
            "Skotizo",
            "Spindel",
            "Tempoross",
            "The Gauntlet",
            "The Corrupted Gauntlet",
            "The Leviathan",
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
        ]  # 58 bosses

        for account in Account.objects.filter(is_active=True):
            response = requests.get(
                f"{settings.OSRS_PLAYER_HISCORES_API}{account.name}"
            )

            if response.status_code == 404:
                raise CommandError(
                    f"{account.name} was not found on the OSRS official hiscores."
                )

            data = [
                line.split(",") for line in response.content.decode("utf-8").split("\n")
            ]

            hiscores = zip(bosses, data[len(skills) + len(activities) :])
            for hiscores_name, hiscore in hiscores:
                try:
                    rank, kc = hiscore
                except ValueError:
                    raise CommandError(
                        f"ValueError: Not enough values to unpack. Account: {account.name} {hiscores_name} values:{hiscores}"
                    )
                try:
                    content = Content.objects.get(hiscores_name__iexact=hiscores_name)
                except Content.DoesNotExist:
                    raise CommandError(
                        f"No Content object exists with hiscores_name={hiscores_name}"
                    )

                obj, created = Hiscores.objects.update_or_create(
                    account=account,
                    content=content,
                    defaults={"kill_count": kc, "rank_overall": rank},
                )
                if created:
                    print(
                        f"Created new Hiscores object {obj.id} for {obj.account} {obj.content} rank:{obj.rank_overall} kc: {obj.kill_count}"
                    )
                else:
                    print(
                        f"Updated Hiscores object {obj.id} for {obj.account} {obj.content} rank:{obj.rank_overall} kc: {obj.kill_count}"
                    )
