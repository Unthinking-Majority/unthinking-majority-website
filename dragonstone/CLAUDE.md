# dragonstone app

Manages the **Dragonstone** rank. It is a high-tier clan rank earned only by accumulating **dragonstone points** ("dstone points") through clan-positive activities. An account "has dragonstone" while its **active** points (accepted and not expired) are at or above `config.DRAGONSTONE_POINTS_THRESHOLD`. Points expire `config.DRAGONSTONE_EXPIRATION_PERIOD` days after their `date`, so members must keep earning to keep the rank.

Clan leaders manage all of this in the Django admin. Discord webhooks tell them when someone crosses the threshold in either direction, so they can change the in-game rank (`Account.rank`).

## Constants (`dragonstone/__init__.py`)

- `DRAGONSTONE_SUBMISSION_TYPES`: `PVM_SPLIT`, `MENTOR`, `EVENT`, `NEW_MEMBER_RAID`, `GROUP_CA`.
- `EVENT_CHOICES`: `PVM`, `SKILLING` (both count as "minor" events for points), `EVENT_MENTOR`, `MAJOR`, `OTHER`. The int values do **not** follow display order (`EVENT_MENTOR=4`).

## Data model

There are two polymorphic hierarchies. **Submissions** are user-submitted and need moderation. **Points** are the actual ledger rows per account. Submissions link to accounts *through* point models: each M2M uses a `through=` points model, so adding an account to a submission creates its points row.

### Submissions (`models/submissions.py`)

**`DragonstoneBaseSubmission`** is a `PolymorphicModel` with the same moderation pattern as achievements:

- Fields: `proof`, `notes`, `denial_notes`, `accepted` (nullable), `date`.
- `on_creation()` posts to `config.UM_DRAGONSTONE_SUBMISSIONS_DISCORD_WEBHOOK_URL` with `dragonstone-accept/deny-submission-<pk>` buttons.
- `save()` calls `on_accepted()` when `accepted` flips to `True`.
- Manager: `accepted()`, `denied()`, and `active()` (not expired, by date).

| Submission | Accounts that earn points (through model) | Other fields | Points from config |
|---|---|---|---|
| `PVMSplitSubmission` | `accounts` → `PVMSplitPoints` (`related_name="points"`) | `content` (`can_be_split`) | `PVM_SPLIT_{difficulty}_PTS` by `content.difficulty` |
| `MentorSubmission` | `mentors` → `MentorPoints` (`mentor_points`) | `learners` (plain M2M, no points), `content` (`can_be_mentored`) | `MENTOR_{difficulty}_PTS` |
| `EventSubmission` | `hosts` → `EventHostPoints`, `participants` → `EventParticipantPoints`, `donors` → `EventDonorPoints` | `name`, `type` (`EVENT_CHOICES`) | `EVENT_{MINOR\|MENTOR\|MAJOR\|OTHER}_{HOSTS\|PARTICIPANTS\|DONORS}_PTS` |
| `NewMemberRaidSubmission` | `accounts` → `NewMemberRaidPoints` | `new_members` (plain M2M; autocomplete limited to `rank__lte=EMERALD`), `content` (raids that `can_be_split`) | `NEW_MEMBER_RAID_PTS` |
| `GroupCASubmission` | `accounts` → `GroupCAPoints` | `ca_tier` (`achievements.CA_CHOICES`), `content` | `GROUP_CA_{ELITE\|MASTER\|GRANDMASTER}_POINTS` |

Each submission type implements `create_new_submission_embed()`, `type_display()`, `value_display()`, `accounts_display()` and `on_accepted()`. `EventSubmission.roles_display(account)` is exposed to templates through the `{% get_event_submission_roles %}` tag in `templatetags/dragonstone_extras.py`.

### Points (`models/points.py`)

**`DragonstonePoints`** is a `PolymorphicModel` with `account` (`related_name="dragonstone_points"`), `points` and `date`. `save()` calls `on_created()` on the first insert.

- **Points are computed and stored when the row is created**, in each child's `save()` (`if not self.pk:`), from `config` and the parent submission. Submission-linked points also copy `submission.date`.
  - Changing a config value later does *not* recompute existing rows by itself. `main/signals.py` handles that by bulk-updating rows when a `Settings` value changes.
  - If you add a new points type or config key, add it to that signal's `objects_mapping`. The `GROUP_CA_*` keys are currently missing from it.
- Standalone points with no submission, created by staff in the admin:
  - `FreeformPoints`: any amount. `created_by` is set automatically to the admin user.
  - `RecruitmentPoints`: `recruited` account, worth `RECRUITER_PTS`.
  - `SotMPoints`: Skill of the Month; `rank` is 1–3 and `skill` is one of `main.SKILLS`.
- Submission-linked points: `PVMSplitPoints`, `MentorPoints`, `EventHostPoints`, `EventParticipantPoints`, `EventDonorPoints`, `NewMemberRaidPoints`, `GroupCAPoints`.

`DragonstonePointsQueryset` (`managers.py`):

- `accepted()` includes the standalone types unconditionally, and submission-linked types only when `<type>points__submission__accepted=True`. **When you add a new points type, add it to both `accepted()` and `active()`.**
- `active()` is `accepted()` restricted to rows that are not expired.
- `expired(expired=True, delta=timedelta(0))` filters by the expiry cutoff, shifted by `delta`.

### Totals and caps

The total per account is computed by `Account.objects.dragonstone_points()` in `account/managers.py`. That is the single source of truth. `PVMSplitPoints` and `GroupCAPoints` **share a cap** of `config.CAPPED_POINTS_MAX`; all other types are uncapped. `Account.get_dragonstone_pts(ignore=[...])` and `Account.dragonstone_expiration_date()` build on it.

## Rank-change notifications

Rank changes are detected by comparing totals before and after an event:

- **Gain via submission:** `<Submission>.on_accepted()` loops over its points rows and compares `get_dragonstone_pts()` against `get_dragonstone_pts(ignore=[pt.pk])`. `EventSubmission` ignores all of an account's host, participant and donor rows together. If the account crossed the threshold, it calls `account.notify_dstone_status_change()`, which posts to `settings.DRAGONSTONE_UPDATES_DISCORD_WEBHOOK_URL`.
- **Gain via standalone points:** `on_created()` does the same threshold check.
- **Gain via points added in admin to an already-accepted submission:** the child `on_created()` handles this case (it checks `self.submission.accepted`).
- **Loss via expiry:** the `notify_dstone_loss` management command runs **hourly** on a scheduler. It compares `dragonstone_points()` now against `dragonstone_points(delta=-1h)` and notifies accounts that dropped below the threshold. If the schedule interval changes, change the delta to match.

## Submission wizard (`views.py`, `forms.py`)

`DragonstoneSubmissionWizard` lives at `dragonstone:submit-dragonstone` (`/dragonstone/submit/`). Step 1 is `dragonstone_submission_type_form`, then exactly one type-specific form, chosen through `condition_dict`. Templates are in `templates/dragonstone/forms/wizard/`.

- Every ModelForm overrides `save()` with a custom `save_m2m`. It **creates the through points rows explicitly** (e.g. `PVMSplitPoints.objects.create(account=..., submission=instance)`) instead of letting Django set the M2M. That makes each points row's `save()` run and compute its value. Keep this pattern.
- `proof` is required on all forms.
- Autocomplete filters: accounts use `is_active=True`, content uses `can_be_split` or `can_be_mentored`, and new-member raids use `category__name__iexact=Raids`.

## Other URLs

`dragonstone:points-breakdown` is a static `TemplateView` that explains how many points each activity gives, reading the values from `config`.

## Admin (`admin/`)

- `admin/submissions.py`: one admin per submission type, with **tabular inlines of the points rows** (`admin/inlines.py`) so staff can add or remove accounts after the fact. The inline `points` field is read-only because it is computed.
- `admin/points.py`: admins for every points type, plus "All Dragonstone Points". Freeform, Recruitment and SotM points are created directly here.
- `AccountAdmin` (in `account/admin.py`) is where leaders see each account's current dstone total and icon.

## API (`api/`)

Route: `dragonstone-base-submissions`. The Discord bot uses it to accept or deny submissions from button presses.
