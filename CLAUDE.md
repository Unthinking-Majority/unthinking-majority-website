# CLAUDE.md

Website for the Old School RuneScape (OSRS) clan **Unthinking Majority** ("UM"), live at https://www.um-osrs.com.

The site does two jobs:

1. **Leaderboards / achievements.** Clan members submit personal bests (PBs), pets, collection logs and combat achievement tiers. Staff accept or deny them in the Django admin, and accepted submissions show up on public leaderboards. Official OSRS hiscores are also synced and shown per boss/activity.
2. **Dragonstone rank management.** "Dragonstone" is a high-tier clan rank earned only through **dragonstone points** ("dstone points"). Members earn them by splitting PvM drops, mentoring, hosting or attending events, running new-member raids, completing group CAs, recruiting, and so on. Points expire after a configurable period. Clan leaders use the admin to see who holds the rank, and Discord webhooks announce when someone gains or loses it.

Each Django app has its own `CLAUDE.md` with details. Read the relevant one before changing an app:

| App | Purpose |
|---|---|
| [`main/`](main/CLAUDE.md) | Core shared models (`Content`, `Board`, `Pet`, `Settings`), leaderboard views, Wagtail CMS pages, dynamic `config`, navbar, shared widgets/autocomplete |
| [`account/`](account/CLAUDE.md) | `Account` (an in-game player), linking to Django `User`, moderated sign-up, profile, and the points-aggregation querysets |
| [`achievements/`](achievements/CLAUDE.md) | PB/pet/collection log/CA submissions, the submission wizard, OSRS hiscores sync |
| [`dragonstone/`](dragonstone/CLAUDE.md) | Dragonstone submissions and points, expiry, rank-change notifications |
| [`bounty/`](bounty/CLAUDE.md) | Time-limited "Bounty" PB competitions on a single board with a GP prize pool |
| [`theme/`](theme/CLAUDE.md) | django-tailwind theme app: Tailwind config, CSS source, base template, fonts, form component tags |

`um/` is the Django project package (settings, root URLconf, WSGI, custom admin site, and the `get_file_path` upload helper). It is not an app.

## Tech stack

- **Python ~3.12**, dependencies managed with **Poetry** (`pyproject.toml`, `poetry.lock`; `package-mode = false`).
- **Django ~5.2**, with **PostgreSQL** only. The code uses Postgres-specific features (`StringAgg`, `.distinct("field")`), so SQLite will not work.
- **Tailwind CSS v3** via **django-tailwind** (`TAILWIND_APP_NAME = "theme"`), with the `@tailwindcss/typography`, `forms` and `line-clamp` plugins and PostCSS (`postcss-import`, `postcss-nested`, `postcss-simple-vars`). There is no JS framework. Frontend JS is plain vanilla scripts plus `autoComplete.js`, loaded from a CDN.
- **Wagtail ~7.0** CMS for the home page and generic content pages. The editor is at `/cms/`.
- **Django REST Framework** API at `/api/`, using token auth and `DjangoModelPermissions`, with `django-filter`.
- **django-polymorphic** for the submission and points hierarchies.
- **django-formtools** `SessionWizardView` for the multi-step submission forms.
- **django-notifications-hq** (pinned git rev) for in-site notifications, subclassed as `main.UMNotification`.
- Admin extras: **django-adminactions** (mass update etc.) and **django-admin-autocomplete-filter** (`AutocompleteFilterFactory`, old and unmaintained, and the owner wants to drop it eventually).
- Prod: **Heroku** (`Procfile`: `release: python manage.py migrate`, `web: gunicorn um.wsgi`), **WhiteNoise** for static files, **S3** via `django-storages`/`boto3` for media, **Sentry**.
- Dev only (loaded when `DEBUG=True`): `django-debug-toolbar`, `django-browser-reload`, `django-extensions`.
- Formatting: **black** for Python and **djlint** for Django templates. Both are dev dependencies; follow their style.

## Local development

See `setup.md` for first-time setup. In short:

```bash
source bin/debug.sh              # exports env vars (bin/ is gitignored; never commit it)
./manage.py tailwind install     # first time: installs theme/static_src node deps
./manage.py tailwind start       # Tailwind watcher (rebuilds theme/static/css/dist/styles.css)
./manage.py runserver            # in another terminal
```

- A local Postgres DB is restored from a prod dump. `bin/restore_local_db.sh [--new]` drops the local DB and restores it, and `--new` first pulls a fresh backup from Heroku. **This is destructive. Don't run it unless asked.**
- The built CSS (`**/dist/styles.css`) is gitignored. Heroku builds it through the root `package.json` `heroku-postbuild` script.
- There is **no test suite**. To sanity-check changes, use `./manage.py check`, `./manage.py makemigrations --check --dry-run`, and load the affected pages or admin.

### Required environment variables

`SECRET_KEY`, `DEBUG` (parsed with `literal_eval`, so it must be `"True"`/`"False"`), `DOMAIN`, `MAX_COL_LOG` (int, **required at import time**: settings crash without it), `OSRS_PLAYER_HISCORES_API`, `STATIC_HOST`, the Discord webhooks `UM_PB_DISCORD_WEBHOOK_URL`, `BOUNTY_DISCORD_WEBHOOK_URL` and `DRAGONSTONE_UPDATES_DISCORD_WEBHOOK_URL`, and the DB variables (`LOCAL_DB_NAME`, `LOCAL_DB_USERNAME`, `LOCAL_DB_PASSWORD`, `PORT` in debug; `DATABASE_URL` in prod). Prod also uses `AWS_*` and `SENTRY_DSN`.

## Architecture and cross-cutting conventions

- **Two kinds of configuration:**
  - `django.conf.settings`: env-driven, static, and holds secrets.
  - `main.config.config`: DB-driven key/value rows in `main.Settings`, editable by admins at runtime. `config.SOME_KEY` does a DB query on every access, casts numeric strings to `int`, and raises `AttributeError` if the key row doesn't exist. Point values, thresholds, expiry periods and some Discord webhook URLs live here. See `main/CLAUDE.md` for the key list.
- **Submission moderation pattern** (used by achievements, dragonstone and account sign-up):
  - `accepted` is a nullable boolean: `None` means pending, `True` accepted, `False` denied.
  - Creating a submission calls `on_creation()`, which posts a Discord embed with Accept/Deny **button components**. The button `custom_id`s (e.g. `achievement-accept-submission-<pk>`, `dragonstone-deny-submission-<pk>`, `bounty-accept-<pk>`) are handled by the clan's Discord bot, which lives outside this repo and talks to the site through the REST API. **Don't rename these IDs without coordinating.**
  - `save()` compares against the original `accepted` value, and a change to `True` fires `on_accepted()`.
  - When an admin changes `accepted`, `send_notifications(request)` creates `UMNotification`s for the linked users.
- **Polymorphic base classes** are `achievements.BaseSubmission`, `dragonstone.DragonstoneBaseSubmission` and `dragonstone.DragonstonePoints`. Base-class methods delegate to `self.get_real_instance()`. Each child type implements `type_display()`, `value_display()` and `accounts_display()` (plus `on_accepted()` / `on_created()`).
- **File uploads** use `upload_to=um.functions.get_file_path`, which reads the model's `UPLOAD_TO` class attribute and stores the file under a UUID filename.
- **Choice constants** live in each app's `__init__.py` as `range()`-based ints, for example `main.TIME`/`EASY`/`SKILLS`, `achievements.RECORD`/`GRANDMASTER`, `dragonstone.PVM_SPLIT`/`MAJOR`, `account.DRAGONSTONE`/`EMERALD`. Import them from the app package.
- **Frontend:** templates extend `theme/templates/base.html` → `main/templates/main/site_base.html`. Style with Tailwind utility classes directly in templates. Reusable pieces are template tags (`um_components`, `main_extras`, `landing_leaderboards`) and partial templates. Details are in `theme/CLAUDE.md`.
- **Autocomplete:** the custom widgets `main.widgets.AutocompleteSelectWidget` and `AutocompleteSelectMultipleWidget` call simple JSON endpoints (`account-autocomplete`, `content-autocomplete`, `pet-autocomplete`). These endpoints turn **any GET param into an ORM filter**, so forms narrow the results with query strings such as `?is_active=True&rank__lte=1`.
- **Admin** is the primary staff tool. It uses the custom `um.admin.UMAdminSite` (nav sidebar disabled). `templates/admin/actions.html` adds a Save button next to changelist actions for `list_editable` pages.

## URL map (root `um/urls.py`)

| Prefix | Target |
|---|---|
| `/` | `main.urls` (leaderboards, notifications, autocomplete), then the Wagtail catch-all |
| `/achievements/` | `achievements` namespace (submission wizard, points multipliers) |
| `/dragonstone/` | `dragonstone` namespace (submission wizard, points breakdown) |
| `/bounty/` | `bounty` namespace |
| `/accounts/` | account URLs. The instance namespace is `account` and the app namespace is `accounts`, so **both `account:` and `accounts:` reverse**. The code mostly uses `accounts:` |
| `/api/` | DRF `DefaultRouter` merging the `main`, `account`, `achievements` and `dragonstone` routers |
| `/admin/`, `/cms/`, `/adminactions/`, `/documents/`, `/inbox/notifications/` | Django admin, Wagtail admin, adminactions, Wagtail docs, notifications |

## Management commands (run on a scheduler in prod)

- `notify_dstone_loss` (dragonstone): run **hourly**. It posts Discord updates for accounts whose dstone rank lapsed through point expiry in the last hour.
- `sync_hiscores` (achievements): pulls OSRS hiscores for all active accounts and upserts `Hiscores`.
- `merge_accounts <main> <other>...` (main): re-points every relation from the duplicate accounts to the main account, then deletes the duplicates.

## Git conventions

Commits use Conventional Commits prefixes: `feat:`, `fix:`, `refactor:`, `style:`, `chore:`, and `feat!:` for breaking changes. Keep the subject short and lowercase.

## Gotchas

- `MAX_COL_LOG` is baked into `ColLogSubmission.col_logs` validators, so changing the env var generates a new migration in `achievements`. That is expected.
- Migrations are committed. Always run `makemigrations` after changing models, and review the output.
- Tailwind only compiles classes it can find in templates, JS or Python files. Class names built dynamically (e.g. `bg-um-{{ theme }}`) must be covered by the `safelist` in `theme/static_src/tailwind.config.js`.
- The `[tool.django-stubs]` settings module in `pyproject.toml` (`MainApplication.settings`) is stale. The real module is `um.settings`.
