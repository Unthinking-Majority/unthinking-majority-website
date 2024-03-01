TIME, INTEGER, DECIMAL = range(3)
METRIC_CHOICES = (
    (TIME, "Time"),
    (INTEGER, "Integer"),
    (DECIMAL, "Decimal"),
)

EASY, MEDIUM, HARD, VERY_HARD = range(4)
DIFFICULTY_CHOICES = (
    (EASY, "Easy"),
    (MEDIUM, "Medium"),
    (HARD, "Hard"),
    (VERY_HARD, "Very Hard"),
)

THEME_CHOICES = (
    ("green", "Green"),
    ("purple", "Purple"),
    ("brown", "Brown"),
)

(
    ATTACK,
    DEFENCE,
    STRENGTH,
    HITPOINTS,
    RANGED,
    PRAYER,
    MAGIC,
    COOKING,
    WOODCUTTING,
    FLETCHING,
    FISHING,
    FIREMAKING,
    CRAFTING,
    SMITHING,
    MINING,
    HERBLORE,
    AGILITY,
    THIEVING,
    SLAYER,
    FARMING,
    RUNECRAFTING,
    HUNTER,
    CONSTRUCTION,
) = range(23)
SKILLS = (
    (ATTACK, "Attack"),
    (DEFENCE, "Defence"),
    (STRENGTH, "Strength"),
    (HITPOINTS, "Hitpoints"),
    (RANGED, "Ranged"),
    (PRAYER, "Prayer"),
    (MAGIC, "Magic"),
    (COOKING, "Cooking"),
    (WOODCUTTING, "Woodcutting"),
    (FLETCHING, "Fletching"),
    (FISHING, "Fishing"),
    (FIREMAKING, "Firemaking"),
    (CRAFTING, "Crafting"),
    (SMITHING, "Smithing"),
    (MINING, "Mining"),
    (HERBLORE, "Herblore"),
    (AGILITY, "Agility"),
    (THIEVING, "Thieving"),
    (SLAYER, "Slayer"),
    (FARMING, "Farming"),
    (RUNECRAFTING, "Runecrafting"),
    (HUNTER, "Hunter"),
    (CONSTRUCTION, "Construction"),
)
