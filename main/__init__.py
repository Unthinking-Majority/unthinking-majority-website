TIME, INTEGER, DECIMAL = range(3)
METRIC_CHOICES = (
    (TIME, 'Time'),
    (INTEGER, 'Integer'),
    (DECIMAL, 'Decimal'),
)

RECORD, PET, COL_LOG, CA = range(4)
SUBMISSION_TYPES = (
    (RECORD, 'Record'),
    (PET, 'Pet'),
    (COL_LOG, 'Collection Log'),
    (CA, 'Combat Achievement'),
)

GRANDMASTER, MASTER, ELITE = range(3)
CA_CHOICES = (
    (GRANDMASTER, 'Grandmaster'),
    (MASTER, 'Master'),
    (ELITE, 'Elite'),
)
CA_DICT = {
    GRANDMASTER: 'Grandmaster',
    MASTER: 'Master',
    ELITE: 'Elite',
}
