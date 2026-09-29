# achievements app

Handles leaderboard submissions: personal bests (PB records), pets, collection logs, and combat achievement (CA) tiers. It also stores synced official OSRS hiscores. This data drives the public leaderboards in `main` and the achievement points in `account.managers.AccountQueryset.annotate_points()`.

## Constants (`achievements/__init__.py`)

- `SUBMISSION_TYPES`: `RECORD`, `PET`, `COL_LOG`, `CA`.
- `CA_CHOICES` / `CA_DICT`: `GRANDMASTER=0`, `MASTER=1`, `ELITE=2`. **A lower int is a better tier**, so "best tier" means `Min("ca_tier")` or ascending order. The dragonstone `GroupCASubmission` reuses these constants.

## Models (`models.py`)

**`BaseSubmission`** is a `PolymorphicModel` and the parent of every achievement submission.

- Fields: `proof` (image), `notes`, `denial_notes`, `accepted` (`None` pending, `True`, or `False`), `date`.
- Default ordering is `-date` with nulls last.
- Manager `SubmissionQueryset` (`managers.py`) provides `accepted()` and `denied()`. It also has `active()`, which keeps only submissions where at least half of the accounts are still `is_active`. It relies on the M2M `accounts`, so only `RecordSubmission` supports it.
- `save()` calls `get_real_instance().on_accepted()` when `accepted` flips to `True`.
- `on_creation()` posts a Discord embed with buttons to `config.UM_ACHIEVEMENT_SUBMISSIONS_DISCORD_WEBHOOK_URL`.
  - Button ids: `achievement-accept-submission-<pk>` and `achievement-deny-submission-<pk>`.
  - If a record belongs to the **current bounty's board**, the ids become `bounty-deny-achievement-accept/deny-<pk>` and an extra "Accept Bounty" button (`bounty-accept-<pk>`) is added. These ids are consumed by the external Discord bot, so don't change them casually.
- `type_display()`, `value_display()` and `accounts_display()` delegate to the child class, and every child must implement them. They also need `send_notifications(request)` and `on_accepted()`.

Child models:

| Model | Fields | Notes |
|---|---|---|
| `RecordSubmission` | `accounts` (M2M), `board` (FK `main.Board`, `related_name="submissions"`), `value` (Decimal, seconds when the metric is TIME), `bounty_accepted` | `value_display()` formats TIME as `m:ss.xx`. `on_accepted()` posts to `settings.UM_PB_DISCORD_WEBHOOK_URL` with the leaderboard rank, and notifies the current bounty if `bounty_accepted` is set |
| `PetSubmission` | `account`, `pet` | One row per pet. The form creates several rows sharing one proof file |
| `ColLogSubmission` | `account`, `col_logs` | Validated against `settings.MAX_COL_LOG`, so changing that env var creates a migration |
| `CASubmission` | `account`, `ca_tier` | |

**`Hiscores`** holds official OSRS hiscore data per account and content: `score` (kill count) and `rank_overall`. It is `unique_together (account, content)`, ordered by `-score`. `main.LeaderboardView` shows it for `?type=hiscores`.

## Submission wizard (`views.py`, `forms.py`)

`SubmissionWizard` (formtools `SessionWizardView`) lives at `achievements:submit-achievement` (`/achievements/submit/`). Steps are enabled through `condition_dict`:

1. `submission_type_form` picks the type.
2. For records:
   - `select_content_form` offers content with `has_pbs=True`.
   - `select_board_form` appears only if that content has more than one board.
   - `record_submission_form` takes the entry, with `board` passed via `get_form_kwargs`.
3. Otherwise one of `pet_submission_form`, `col_logs_submission_form` or `ca_submission_form`.

`done()` saves the submission and calls `on_creation()` on each instance.

Other details:

- Uploaded files are staged in `MEDIA_ROOT/temp_files` between steps.
- POSTing `wizard_goto_step` clears the current step's data before navigating back.
- Templates live in `templates/achievements/forms/wizard/` and extend `main/forms/wizard/base.html`.
- `get_form_initial` pre-fills `account` with `request.user.account` when logged in. The forms then **hide the account autocomplete** (they check `"account" not in initial`).

Form validation rules to preserve:

- `RecordSubmissionForm`:
  - The time comes in as `minutes` + `seconds`, or as a raw `value` for non-TIME metrics, and must be greater than 0.
  - The number of accounts must equal `board.team_size`, and all accounts must be active.
  - Solo boards use the single `account` field, which is copied into `accounts`.
  - `proof` is required.
- `PetSubmissionForm` rejects pets the account already has accepted (or pending).
- `ColLogSubmissionForm` requires the value to be at most `MAX_COL_LOG` and greater than the account's current best.
- Every form requires the account to be active.
- `RecordSubmissionChangelistAdminForm` (admin changelist formset): if a record on the current bounty's board is accepted or denied, `bounty_accepted` must also be set.

## Other URLs

`achievements:points-multipliers` is a static `TemplateView` listing the active PB boards with their `points_multiplier` and the `config` place points.

## Admin (`admin.py`)

There is one admin per submission type, plus "All Submissions" (`BaseSubmissionAdmin`) and `HiscoresAdmin`.

- Every submission admin overrides `save_model` to call `obj.send_notifications(request)` when `accepted` changes. That creates `UMNotification`s for the linked users. **Keep this when adding new submission types.**
- `RecordSubmissionAdmin` annotates `has_bounty` and uses the bounty-aware changelist formset.

## API (`api/`)

- `base-submissions`.
- `record-submissions`, with a `record-submissions/<pk>/in_active_bounty/` action the Discord bot uses to decide how to handle bounty buttons.
- Serializers include `admin_url`.

## Management commands

`sync_hiscores` fetches `settings.OSRS_PLAYER_HISCORES_API + <name>` for every active account, using aiohttp with at most 10 concurrent requests.

- It matches each returned `activities[].name` to `Content.hiscores_name` (case-insensitive) and skips names with no match.
- It bulk-upserts `Hiscores` (`update_conflicts` on `account, content`).
- Accounts whose IGN is not found (non-200 responses) are printed and skipped.
