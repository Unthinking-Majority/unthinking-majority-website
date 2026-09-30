<h2 align="center">Website for the Old School Runescape Clan, Unthinking Majority. </h2>

[![Static Badge](https://img.shields.io/badge/chat-discord-%237289DA)](https://discord.gg/umcc)
[![Static Badge](https://img.shields.io/badge/framework-django-%230C4B33)](https://www.djangoproject.com/)


https://www.um-osrs.com/

## How it fits together

- **Django 5.2** site (`um/` is the project package) with an app per feature: `account` (clan accounts and website sign-up), `achievements` (leaderboards, hiscores, achievement submissions), `dragonstone` (dragonstone points and submissions), `bounty` (bounty events) and `main` (content, boards, settings, notifications, the REST API).
- **Wagtail 8** at `/cms/` for editable pages such as the home page. The Django admin at `/admin/` is where staff do everything else.
- **Tailwind CSS 3** via django-tailwind, built from `theme/static_src`.
- **Postgres** on Heroku, with media uploads on S3. `migrate` runs in the release phase (`Procfile`).
- **Discord:** new submissions are posted to moderation channels through webhooks, with Accept/Deny buttons. Those buttons are handled by the [Discord bot](https://github.com/Unthinking-Majority/unthinking-majority-discord-bot), which calls back into this site's REST API (`/api/`) with a token.
- Point values, thresholds and the moderation webhook URLs are stored in the `Settings` table and edited in the admin. See [setup.md](setup.md) for the full list and the scheduled jobs.

## Running locally

Follow [setup.md](setup.md) (Python 3.12 with Poetry, Node 24, Postgres restored from a dump), then:

```sh
poetry run ./manage.py tailwind start   # rebuilds CSS on change
poetry run ./manage.py runserver
```

## Admin notes

- **Password resets:** there's no self-service reset. Staff set a new password for the user in the Django admin (`/admin/auth/user/` → the user → "Reset password").
