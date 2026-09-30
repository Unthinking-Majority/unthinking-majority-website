<h2 align="center">Website for the Old School Runescape Clan, Unthinking Majority. </h2>

[![Static Badge](https://img.shields.io/badge/chat-discord-%237289DA)](https://discord.gg/umcc)
[![Static Badge](https://img.shields.io/badge/framework-django-%230C4B33)](https://www.djangoproject.com/)


https://www.um-osrs.com/

## How it fits together

- **Django 5.2 + PostgreSQL**, hosted on Heroku. Staff moderate everything in the Django admin at `/admin/`.
- **Wagtail** CMS for the home page and content pages, edited at `/cms/`.
- **Tailwind CSS** through django-tailwind (the `theme` app). Heroku builds the CSS during deploy.
- **REST API** at `/api/` (Django REST Framework, token auth), used by the clan's [Discord bot](https://github.com/Unthinking-Majority/unthinking-majority-discord-bot).
- Submissions (PBs, pets, collection logs, dragonstone points, sign-ups) post to Discord through webhooks with Accept/Deny buttons. The bot handles the buttons and updates the site through the API.

Each app has a `CLAUDE.md` describing its models and conventions.

## Running locally

Full first-time setup is in [setup.md](setup.md). In short:

```bash
poetry install
source bin/debug.sh           # your local env vars, see setup.md
./manage.py tailwind install  # first time only
./manage.py tailwind start    # Tailwind watcher
./manage.py runserver         # in another terminal
```

There's no test suite. `./manage.py check` and `./manage.py makemigrations --check --dry-run` are the quick sanity checks.
