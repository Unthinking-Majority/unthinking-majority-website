# Help file for setting up environment

- Create python virtual environment
    - Install python packages from requirements.txt

- Make a debug.sh file under /bin/
    - Need to set the following environment variables:
        - LOCA_DB_NAME to name of local postgres database
        - LOCAL_DB_USERNAME to name of user who owns local postgres database
        - LOCAL_DB_PASSWORD to password of local user who owns local postgres database
        - SECRET_KEY to a django secret key
        - STATIC_HOST=""
        - DEBUG="True"
        - MAX_COL_LOG to whatever current max collection log number is
        - UM_PB_DISCORD_WEBHOOK_URL to a webhook for a test channel on a test server.
        - HEROKU_APP="unthinking-majority"
        - OSRS_PLAYER_HISCORES_API="https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player="

- Install postgres (any version should be fine)
    - install libpq-dev
    - Restore local database with a provided postgres dump file from someone who can get you one!

- Install nodejs + npm
    - install node packages

- Run `./manage.py tailwind install` to install all tailwind css dependencies