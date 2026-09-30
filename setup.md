# Help file for setting up environment

- Install Python 3.12 and [Poetry](https://python-poetry.org/)
  - Install python packages with `poetry install`

- Make a debug.sh file under /bin/
  - Need to set the following environment variables:
    - LOCAL_DB_NAME to name of local postgres database
    - LOCAL_DB_USERNAME to name of user who owns local postgres database
    - LOCAL_DB_PASSWORD to password of local user who owns local postgres database
    - PORT to the port of the local postgres server (e.g. 5432)
    - SECRET_KEY to a django secret key
    - STATIC_HOST=""
    - DEBUG="True"
    - DOMAIN to the host used in links posted to Discord and returned by the API (e.g. "localhost:8000")
    - MAX_COL_LOG to whatever current max collection log number is
    - UM_PB_DISCORD_WEBHOOK_URL, BOUNTY_DISCORD_WEBHOOK_URL and DRAGONSTONE_UPDATES_DISCORD_WEBHOOK_URL to webhooks for test channels on a test server.
    - HEROKU_APP="unthinking-majority"
    - OSRS_PLAYER_HISCORES_API="<https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=>"
  - Production only (set as Heroku config vars, not needed locally):
    - DATABASE_URL (set by the Heroku Postgres add-on)
    - AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_CUSTOM_DOMAIN for media uploads
    - SENTRY_DSN

- Install postgres (any version should be fine)
  - install libpq-dev
  - Restore local database with a provided postgres dump file from someone who can get you one!

- Install nodejs 24 + npm
  - install node packages (`npm ci`)

- Run `./manage.py tailwind install` to install all tailwind css dependencies

## Settings stored in the database

Point values, thresholds and some Discord webhooks live in the `Settings` table (edited in `/admin/`), not in environment variables. A restored dump already has them. On an empty database, every key below needs a row, or the pages that read it will error:

- Discord webhooks: `UM_ACHIEVEMENT_SUBMISSIONS_DISCORD_WEBHOOK_URL`, `UM_DRAGONSTONE_SUBMISSIONS_DISCORD_WEBHOOK_URL`, `UM_USER_CREATION_SUBMISSIONS_DISCORD_WEBHOOK_URL`. The Discord bot overwrites these on startup.
- Dragonstone: `DRAGONSTONE_POINTS_THRESHOLD`, `DRAGONSTONE_EXPIRATION_PERIOD` (days), `CAPPED_POINTS_MAX`
- `RECRUITER_PTS`, `NEW_MEMBER_RAID_PTS`
- `SOTM_FIRST_PTS`, `SOTM_SECOND_PTS`, `SOTM_THIRD_PTS`
- `PVM_SPLIT_EASY_PTS`, `PVM_SPLIT_MEDIUM_PTS`, `PVM_SPLIT_HARD_PTS`, `PVM_SPLIT_VERY_HARD_PTS`
- `MENTOR_EASY_PTS`, `MENTOR_MEDIUM_PTS`, `MENTOR_HARD_PTS`, `MENTOR_VERY_HARD_PTS`
- `EVENT_MINOR_HOSTS_PTS`, `EVENT_MINOR_PARTICIPANTS_PTS`, `EVENT_MINOR_DONORS_PTS`
- `EVENT_MENTOR_HOSTS_PTS`, `EVENT_MENTOR_PARTICIPANTS_PTS`, `EVENT_MENTOR_DONORS_PTS`
- `EVENT_MAJOR_HOSTS_PTS`, `EVENT_MAJOR_PARTICIPANTS_PTS`, `EVENT_MAJOR_DONORS_PTS`
- `EVENT_OTHER_HOSTS_PTS`, `EVENT_OTHER_PARTICIPANTS_PTS`, `EVENT_OTHER_DONORS_PTS`
- `GROUP_CA_ELITE_POINTS`, `GROUP_CA_MASTER_POINTS`, `GROUP_CA_GRANDMASTER_POINTS`
- `FIRST_PLACE_PTS`, `SECOND_PLACE_PTS`, `THIRD_PLACE_PTS`, `FOURTH_PLACE_PTS`, `FIFTH_PLACE_PTS`

Production also has a `PVM_SPLIT_POINTS_MAX` row, which nothing reads any more.

## Scheduled jobs

These run from Heroku Scheduler in production:

- `./manage.py notify_dstone_loss` must run **hourly**. It posts to the dragonstone updates channel for accounts that lost dragonstone rank because their points expired in the last hour, so the schedule and the one-hour window have to match.
- `./manage.py sync_hiscores` pulls OSRS hiscores for every active account and updates the hiscores leaderboards.
