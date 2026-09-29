# main app

The core shared app. It holds the content taxonomy that every other app hangs off, the public leaderboard views, the Wagtail CMS pages, the DB-backed runtime `config`, notifications, and shared UI plumbing (navbar, autocomplete widgets, template filters).

## Models (`main/models/`)

`models/__init__.py` star-imports `models.py` and `pages.py`, so import models as `from main.models import Board`.

### Content taxonomy (`models/models.py`)

- **`ContentCategory`**: groups content in the navbar (e.g. Raids, Bosses). `active_content()` returns contents with `has_pbs=True` OR `has_hiscores=True`.
- **`Content`**: a boss or activity (e.g. "Chambers of Xeric").
  - `difficulty` (`EASY`..`VERY_HARD`) sets the dragonstone point values for splits and mentoring.
  - Flags: `has_pbs` (it has PB boards), `has_hiscores` (it is on the official OSRS hiscores; `hiscores_name` must match the hiscores name, case-insensitively), `can_be_mentored`, `can_be_split`. The flags gate which content appears in each submission form's autocomplete.
  - Other fields: `slug`, `icon`, and `order` (navbar position 1–12; blanks sort last).
  - `leaderboard_url()` reverses `leaderboard`.
- **`Board`**: one PB leaderboard for a `Content`, e.g. "Solo" or "Trio". A content can have several boards.
  - Fields: `team_size` (1–8), `metric` (`TIME`/`INTEGER`/`DECIMAL`) plus `metric_name`, `points_multiplier` (0–3, scales achievement points), `is_active`, `slug`, `order`.
  - `submissions_ordering` is `""` for ascending (lower is better, e.g. times) and `"-"` for descending. It is prefixed onto `value` in `order_by`, so reuse it rather than hard-coding a sort direction.
  - `top_unique_submissions(start_date, end_date, exclude_inactive, bounty_accepted)` is the key leaderboard query. It returns the best accepted submission **per unique team** (teams are identified by `StringAgg` of the account names). Leaderboards, points, bounty and the API all use it.
  - `__str__` includes the content name only when the content has more than one board.
- **`Pet`**: an OSRS pet with an icon. Used by pet submissions.
- **`UMNotification`**: subclass of django-notifications `Notification` with `custom_url`. The stock `Notification` admin is unregistered in favour of this one.
- **`Settings`**: a key/value row for runtime config (see below).

### Wagtail pages (`models/pages.py`, `blocks.py`)

- **`HomePage`**: singleton (`max_count = 1`) with `logo` and a `body` StreamField of `BannerBlock`s. The template `main/home_page.html` also renders the landing leaderboards.
- **`ContentPage`**: generic CMS page, used for things like PvM resource guides.
  - Fields: `author` (blank means it is derived from revision authors via `get_page_authors`), `theme` (one of `THEME_CHOICES`: green, purple or brown, which map to the `um-*` Tailwind colours), `show_page_index` (sidebar table of contents).
  - `body` StreamField block types: heading_2, heading_3, rich_text, image, embed, emoji_row.
- Custom blocks: `BannerBlock`, `EmojiRowBlock`, and `EmbedBlock`, which is a `URLBlock` rendered through the overridden `{% embed %}` tag that accepts `max_height`.
- The navbar lists root-page children that have `show_in_menus=True`.

## Runtime config (`config.py`, `signals.py`)

`from main.config import config`, then `config.DRAGONSTONE_POINTS_THRESHOLD`.

- Each attribute access queries `Settings` by key, and a missing key raises `AttributeError`.
- A new key needs a `Settings` row created in the admin (or a data migration). A code change alone is not enough.
- Keys in use:
  - Dragonstone thresholds: `DRAGONSTONE_POINTS_THRESHOLD`, `DRAGONSTONE_EXPIRATION_PERIOD` (days), `CAPPED_POINTS_MAX`.
  - Dragonstone point values:
    - `RECRUITER_PTS`, `NEW_MEMBER_RAID_PTS`
    - `SOTM_{FIRST,SECOND,THIRD}_PTS`
    - `PVM_SPLIT_{EASY,MEDIUM,HARD,VERY_HARD}_PTS`, `MENTOR_{EASY,MEDIUM,HARD,VERY_HARD}_PTS`
    - `EVENT_{MINOR,MENTOR,MAJOR,OTHER}_{HOSTS,PARTICIPANTS,DONORS}_PTS`
    - `GROUP_CA_{ELITE,MASTER,GRANDMASTER}_POINTS`
  - Achievement points: `{FIRST,SECOND,THIRD,FOURTH,FIFTH}_PLACE_PTS`.
  - Webhooks: `UM_ACHIEVEMENT_SUBMISSIONS_DISCORD_WEBHOOK_URL`, `UM_DRAGONSTONE_SUBMISSIONS_DISCORD_WEBHOOK_URL`, `UM_USER_CREATION_SUBMISSIONS_DISCORD_WEBHOOK_URL`.

`signals.settings_updated` (`pre_save` on `Settings`) back-fills existing dragonstone point rows when a point-value key changes. Dstone points are stored on each row when it is created, so without this signal old rows would keep the old value. **When you add a new points key, add it to `objects_mapping`.** The `GROUP_CA_*_POINTS` keys are currently *not* in the mapping, so changing them only affects new rows.

## Constants (`main/__init__.py`)

- `METRIC_CHOICES` (`TIME`, `INTEGER`, `DECIMAL`)
- `DIFFICULTY_CHOICES` (`EASY`, `MEDIUM`, `HARD`, `VERY_HARD`)
- `THEME_CHOICES`
- `SKILLS`: all OSRS skills including Sailing, **indexed in hiscores order**. Append new skills at the end so existing stored ints don't shift.

## Views and URLs (`views.py`, `urls/`)

| URL name | View | Notes |
|---|---|---|
| `leaderboard` `board/<category>/<content>/` | `LeaderboardView` | `?type=personal-bests\|hiscores`, `?active_board=<slug>` (falls back to the first board if the slug is invalid), `?page=`. 5 per page |
| `pets-leaderboard` | `PetsLeaderboardView` | accounts ranked by accepted pet count |
| `col-logs-leaderboard` | `ColLogsLeaderboardView` | best col-log submission per account (`distinct("account")`) |
| `ca-leaderboard` | `CALeaderboardView` | best CA tier per account (lower int = higher tier) |
| `top-players-leaderboard` | `TopPlayersLeaderboardView` | `Account.objects.annotate_points()` |
| `mark-notification-as-read`, `mark-all-notification-as-read` | JSON endpoints called by `static/js/navbar.js` | |
| `content-autocomplete`, `pet-autocomplete` | `autocomplete.py` | GET params become ORM filters via `prepare_lookup_value` |

Leaderboard views only count **active** accounts (`is_active=True`) and **accepted** submissions. Keep that rule when you add new leaderboards.

## Template tags

- `main_extras`:
  - `{% navbar %}` builds the whole navbar context: categories, CMS menu pages, unread notifications, current bounty.
  - Filters: `gp_display` (e.g. 150000 → `150k`, 12000000 → `12M`; defined in `functions.py`), `addstr`, `mult`, `mult_percentage`.
  - Tags: `settings_value`, `get_page_authors`, `embed`.
- `landing_leaderboards`: top-5 inclusion tags for the home page (`pets_leaderboard`, `col_logs_leaderboard`, `grandmasters_leaderboard`, `recent_submission_leaderboard`, `top_players_leaderboard`). They duplicate some of the queryset logic in `views.py`, so if you change a ranking rule, update both.

## Widgets (`widgets.py`)

`AutocompleteSelectWidget(autocomplete_url, placeholder, label, help_text)` and `AutocompleteSelectMultipleWidget(autocomplete_url, placeholder, label, required)` render `main/widgets/*.html` with autoComplete.js. The forms in achievements, dragonstone and account use them.

## Other templates and static

- `site_base.html` is the layout for every public page: navbar, toast messages, content card.
- `forms/wizard/base.html` is the shared layout for both submission wizards.
- `leaderboard.html`, `leaderboards/`, `landing_leaderboards/`, `navbar/` (desktop and mobile variants), `blocks/`.
- JS in `static/js/`: `navbar.js` (menus and notifications), `forms/loading.js` (submit spinner), `inputmask.js`, `content_page/` (page index sidebar).

## Admin (`admin.py`)

Registers ContentCategory, Content, Board (`points_multiplier` is list-editable), Pet, UMNotification, and Settings (`value` is list-editable). It also calls `adminactions.actions.add_to_site(site)`, which adds mass update and export to every model admin.

## API (`api/`)

Routes: `content-categories`, `contents`, `boards` (plus the `boards/<pk>/top_unique_submissions/` action), and `settings` (filterable by `key`).

## Management commands

`merge_accounts <main_account> <other_accounts...>` walks the reverse FK, M2M and O2O relations of each duplicate `Account`, re-points them to the main account (excluding `hiscores`, which is unique per account and content), then deletes the duplicate.
