# Help file for setting up environment

- Make a debug.sh file under /bin/
    - Need to set the following:
        - LOCA_DB_NAME to name of local postgres database
        - LOCAL_DB_USERNAME to name of user who owns local postgres database
        - LOCAL_DB_PASSWORD to password of local user who owns local postgres database
        - SECRET_KEY
        - STATIC_HOST="""
        - DEBUG="True"
        - MAX_COL_LOG to whatever current max collection log number is
        - UM_PB_DISCORD_WEBHOOK_URL to a webhook for a test channel on a test server.
        - HEROKU_APP="unthinking-majority"
        - WOM_API_KEY to an api key from wiseoldman.net

- Install postgres (any version should be fine)
    - install libpq-dev 

 - Install nodejs + npm

 - Run `./manage.py tailwind install` to install all tailwind css dependencies