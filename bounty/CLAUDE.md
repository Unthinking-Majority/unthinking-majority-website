# bounty app

"Bounty" events are time-limited PB competitions on a single `main.Board`. Clan members race for the best times during the event window, and the top three share a GP prize pool (with optional extra rewards). The theme is Wild West "wanted poster", which is why the western and cast-iron fonts and the `bounty/static/bounty/` images exist.

## Models (`models.py`)

**`Bounty`**:

- `title`, `board` (FK `main.Board`), `start_date`, `end_date`, `image`, `event_phrase` (the in-game phrase that must appear in proof screenshots).
- `prize_pool` (GP int, displayed with the `gp_display` filter).
- Flavour text: `bounty_reason`, `enemy_description`.
- Recorded winners: `first_place`, `second_place`, `third_place` (FK `Account`, `PROTECT`).
- Ordered by `-start_date`.

Methods:

- `Bounty.get_current_bounty()` (classmethod) returns the bounty whose window contains now, or `None`. It is used across the site: navbar, `achievements` submission embeds and buttons, the admin changelist formset, and the API.
- `get_submissions()` returns `board.top_unique_submissions(start_date, end_date, exclude_inactive=False, bounty_accepted=True)`. **Only records with `bounty_accepted=True` count** toward a bounty.
- `on_accepted_submission(submission)` is called from `RecordSubmission.on_accepted()` when the record is `bounty_accepted` during a live bounty. If the record lands in the top 3, it posts a "Bounty Claimed" embed to `settings.BOUNTY_DISCORD_WEBHOOK_URL`.
- `save()` posts a "Bounty Increased" embed whenever `prize_pool` goes up compared with its original value.
- `get_slowest_submission()` exists, and the "slowest time" reward logic is commented out in the model and views. It was used for past events, so keep it for possible reuse. `get_most_improved()` is unimplemented.

**`ExtraBountyReward`** (inline on Bounty) has `title`, `rules`, `percent_of_prize_pool` (0–100) and `winner`. Templates show its share of the pool with `mult_percentage`.

## How a bounty submission flows

1. A member submits a normal record through the achievements wizard on the bounty's board.
2. `BaseSubmission.create_new_submission_components()` sees the live bounty and adds a "🤠 Accept Bounty" button. It also swaps the button ids to `bounty-accept-<pk>` and `bounty-deny-achievement-accept/deny-<pk>`. The external Discord bot handles these.
3. Staff set `accepted` and `bounty_accepted`. In the admin changelist, `RecordSubmissionChangelistAdminForm` forces `bounty_accepted` to be set when moderating a record on the bounty's board.
4. Acceptance triggers the PB webhook and then, if `bounty_accepted`, `Bounty.on_accepted_submission`.

## Views and URLs (`bounty` namespace, `/bounty/`)

| Name | Path | View |
|---|---|---|
| `current-bounty` | `/bounty/` | `CurrentBountyView`: leaderboard for the live bounty. Redirects to `index` if there is no live bounty |
| `index` | `/bounty/index/` | `BountyListView`: past bounties plus the current one |
| `detail` | `/bounty/<pk>/` | `BountyDetail`: leaderboard for a past bounty |
| `rules` | `/bounty/rules/` | `CurrentBountyRulesView` |
| `rules-detail` | `/bounty/rules/<pk>/` | `BountyRulesDetail` |

Templates are in `templates/bounty/`, and `base.html` gives the wanted-poster styling.

## Admin

- `admin/admin.py`: `BountyAdmin` with the `ExtraBountyRewardInline` inline (`admin/inlines.py`) and autocompletes for the board and winners.
- `forms.BountyAdminForm` requires `start_date < end_date` and **forbids overlapping bounties**. `get_current_bounty()` uses `.get()` and assumes at most one live bounty.

There is no API for bounty. The bot uses `achievements`' `record-submissions/<pk>/in_active_bounty/`.
