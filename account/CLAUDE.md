# account app

Represents clan members and links them to website logins. It also holds the heavy aggregation querysets that compute **achievement points** and **dragonstone points** per account.

## Key concept: `Account` vs `User`

- **`Account`** is an **in-game OSRS character / clan member**. Staff create these rows, not users.
  - Fields: `name` (IGN, unique, used for the hiscores lookup), `preferred_name`, `discord_id` (unique, used for `<@id>` mentions in Discord embeds), `is_active` (currently in the clan), `rank`.
  - `rank` is a clan rank from `ACCOUNT_RANK_CHOICES` in `account/__init__.py`: Sapphire, Emerald, Ruby, Diamond, **Dragonstone**, Vanguard, Bronze, Silver, Gold. Lower ranks have lower ints, so `rank__lte=EMERALD` means "new member".
- **`auth.User`** is a website login. It is optionally linked through `Account.user` (O2O, so `request.user.account`). Many accounts have no user; they still appear on leaderboards and can be named in other people's submissions.
- `display_name` returns `preferred_name`, falling back to `name`. Use it for anything user-facing.
- Most achievement and leaderboard logic filters on `is_active=True`. Leaving the clan hides a player without deleting their data.

## Account methods

- `pets()`, `col_logs()` (max accepted), and `ca_tier()` (best accepted tier as a display string).
- `achievements_pts()` is `annotate_points()` for one account.
- `get_dragonstone_pts(ignore=[pk...])` returns current dstone points. `ignore` excludes specific `DragonstonePoints` pks, which lets callers compute a "before" total to detect crossing the threshold.
- `dragonstone_expiration_date()` walks active points newest-first until the running total reaches `DRAGONSTONE_POINTS_THRESHOLD`, then adds `DRAGONSTONE_EXPIRATION_PERIOD` days. It only makes sense for accounts that currently hold dstone, because otherwise `expiration_date` is `None` and adding the timedelta raises.
- `notify_dstone_status_change()` posts to `settings.DRAGONSTONE_UPDATES_DISCORD_WEBHOOK_URL`. The embed says whether the account gained or lost dstone, based on its current points.

## `AccountQueryset` (`managers.py`), used as `Account.objects`

- **`dragonstone_points(ignore=None, delta=timedelta(0))`** annotates `annotated_dragonstone_pts` and orders by it.
  - It sums **accepted, non-expired** `DragonstonePoints` per account and per polymorphic type in Python.
  - `PVMSplitPoints` and `GroupCAPoints` are **capped** together at `config.CAPPED_POINTS_MAX`. All other types are uncapped.
  - The sums are then pushed back in as a `Case/When` annotation.
  - `delta` shifts the expiry cutoff. `notify_dstone_loss` uses `delta=-1h` to compute who held dstone an hour ago.
  - **This is the single source of truth for dstone totals.** Change the rules here, not in templates.
- **`annotate_points()`** annotates achievement `points`.
  - For every active board with `has_pbs`, it takes `board.top_unique_submissions()[:5]` and awards `config.{FIRST..FIFTH}_PLACE_PTS × board.points_multiplier` to each account on that team.
  - An account scores at most once per board.
  - The result is filtered to active accounts and ordered by `-points`.
  - It is expensive (one query set per board). Top-players pages and the landing page call it.

## Sign-up flow (moderated)

Users can't self-register freely. They claim an existing `Account`:

1. `CreateAccountView` / `CreateAccountForm` at `/accounts/create-account/`.
   - The user picks an unclaimed active account through autocomplete (`user__isnull=True`), chooses a username and password, and uploads a screenshot showing a random `phrase` (adjective + animal) typed in game chat.
2. This creates a **`UserCreationSubmission`**. `on_creation()` posts to `config.UM_USER_CREATION_SUBMISSIONS_DISCORD_WEBHOOK_URL` with `user-creation-accept/deny-submission-<pk>` buttons.
3. When staff set `accepted`, `save()` creates the `User` if the submission was accepted, links it to the account, and then **deletes the submission row** whether it was accepted or denied.
   - Note: the raw password is stored on the submission until review. This is a known trade-off of the current design, so don't copy the pattern elsewhere.

## Views and URLs (`urls/`, app_name `accounts`)

- `profile` (login required) has tabs for the user's achievement and dragonstone submissions (`?active_tab=achievements|dragonstone&page=`). It passes `config` into the template for thresholds.
- `create-account` redirects to the profile if the user is already logged in.
- `change-preferred-name` (login required).
- The standard Django auth views are wired to the `account/registration/*.html` templates: login, logout (a POST form, not a GET link), password change and password reset.
- `account-autocomplete` is a JSON endpoint where GET params become ORM filters, e.g. `?is_active=True&rank__lte=1`.

The root URLconf includes this with `namespace="account"` while `app_name = "accounts"`, so both `accounts:profile` and `account:profile` work.

## Admin

- `AccountAdmin` annotates `dragonstone_points()` on the changelist and shows a dragonstone icon when an account is at or above the threshold. This is how leaders see who should hold the rank.
- `rank` and `discord_id` are list-editable.
- `UserCreationSubmissionAdmin` has `accepted` list-editable for quick approval.

## API

- `accounts` (filterable by `discord_id`, used by the Discord bot to map Discord users to accounts; includes `admin_url` and the rank display).
- `user-creation-submissions`.
