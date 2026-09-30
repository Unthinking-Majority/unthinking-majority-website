# Help file for setting up environment

- Install Python 3.12 and [Poetry](https://python-poetry.org/)
  - Install python packages with `poetry install`

- Make a debug.sh file under /bin/ (`bin/` is gitignored, never commit it)
  - Need to set the following environment variables:
    - LOCAL_DB_NAME to name of local postgres database
    - LOCAL_DB_USERNAME to name of user who owns local postgres database
    - LOCAL_DB_PASSWORD to password of local user who owns local postgres database
    - PORT to the port of the local postgres server
    - SECRET_KEY to a django secret key
    - STATIC_HOST=""
    - DEBUG="True"
    - DOMAIN="localhost"
    - MAX_COL_LOG to whatever current max collection log number is
    - UM_PB_DISCORD_WEBHOOK_URL to a webhook for a test channel on a test server.
    - BOUNTY_DISCORD_WEBHOOK_URL to a webhook for a test channel on a test server.
    - DRAGONSTONE_UPDATES_DISCORD_WEBHOOK_URL to a webhook for a test channel on a test server.
    - HEROKU_APP="unthinking-majority"
    - OSRS_PLAYER_HISCORES_API="<https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=>"
  - Production additionally sets DATABASE_URL (set by Heroku), SENTRY_DSN, AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME and AWS_S3_CUSTOM_DOMAIN

- Install postgres (the code uses Postgres-only features, so SQLite will not work)
  - install libpq-dev
  - Restore local database with a provided postgres dump file from someone who can get you one!

- Install nodejs 24 + npm
  - install node packages (`npm ci`)

- Run `./manage.py tailwind install` to install all tailwind css dependencies

## Settings keys

Some config lives in the database instead of env vars, as `Settings` rows edited in the admin (`/admin/main/settings/`). The site errors if one of these keys is missing. A restored dump already has them all:

- Dragonstone: `DRAGONSTONE_POINTS_THRESHOLD`, `DRAGONSTONE_EXPIRATION_PERIOD`, `CAPPED_POINTS_MAX`, `PVM_SPLIT_POINTS_MAX`, `RECRUITER_PTS`, `NEW_MEMBER_RAID_PTS`
- PvM splits: `PVM_SPLIT_EASY_PTS`, `PVM_SPLIT_MEDIUM_PTS`, `PVM_SPLIT_HARD_PTS`, `PVM_SPLIT_VERY_HARD_PTS`
- Mentoring: `MENTOR_EASY_PTS`, `MENTOR_MEDIUM_PTS`, `MENTOR_HARD_PTS`, `MENTOR_VERY_HARD_PTS`
- Events: `EVENT_MINOR_HOSTS_PTS`, `EVENT_MINOR_PARTICIPANTS_PTS`, `EVENT_MINOR_DONORS_PTS`, `EVENT_MENTOR_HOSTS_PTS`, `EVENT_MENTOR_PARTICIPANTS_PTS`, `EVENT_MENTOR_DONORS_PTS`, `EVENT_MAJOR_HOSTS_PTS`, `EVENT_MAJOR_PARTICIPANTS_PTS`, `EVENT_MAJOR_DONORS_PTS`, `EVENT_OTHER_HOSTS_PTS`, `EVENT_OTHER_PARTICIPANTS_PTS`, `EVENT_OTHER_DONORS_PTS`
- Skill of the month: `SOTM_FIRST_PTS`, `SOTM_SECOND_PTS`, `SOTM_THIRD_PTS`
- Group combat achievements: `GROUP_CA_ELITE_POINTS`, `GROUP_CA_MASTER_POINTS`, `GROUP_CA_GRANDMASTER_POINTS`
- Leaderboard placings: `FIRST_PLACE_PTS`, `SECOND_PLACE_PTS`, `THIRD_PLACE_PTS`, `FOURTH_PLACE_PTS`, `FIFTH_PLACE_PTS`
- Discord webhooks, set automatically by the Discord bot when it starts: `UM_ACHIEVEMENT_SUBMISSIONS_DISCORD_WEBHOOK_URL`, `UM_DRAGONSTONE_SUBMISSIONS_DISCORD_WEBHOOK_URL`, `UM_USER_CREATION_SUBMISSIONS_DISCORD_WEBHOOK_URL`

## Scheduled jobs

These run through Heroku Scheduler in production:

- `python manage.py notify_dstone_loss`, every hour. It posts to the dragonstone updates channel when an account loses the rank because its points expired.
- `python manage.py sync_hiscores`. It pulls the OSRS hiscores for every active account.

## Password resets

Accounts don't have email addresses, so there is no self-service password reset. When a member forgets their password, a staff member sets a new one on their user in the Django admin (`/admin/auth/user/` → the user → "Reset password") and passes it on through Discord.
