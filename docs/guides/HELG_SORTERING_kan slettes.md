# Adding a "Helg" sorter group with dagtid / kveld / natt

Adds `helgetimer_natt` to the stats layer, closes a bucket gap, and exposes all
four weekend metrics as sliders on `/turnusliste`.

Work top to bottom — each phase depends on the one before it. The stats column
must exist before the route can publish it.

---

## Background

`app/utils/shift_stats.py` computes three weekend columns today:

| column | rule |
|---|---|
| `helgetimer` | Fri after 17:00 + all of Sat + Sun through Mon 06:00 |
| `helgetimer_dagtid` | Sat/Sun shifts starting before 14:00 |
| `helgetimer_ettermiddag` | Fri-after-17 + Sat/Sun shifts starting 14:00 or later |

Two problems:

1. **No weekend night-hours column.** `natt_helg` is a *count* of night shifts
   on Fri/Lør/Søn (121 in R26), not hours.
2. **A bucket gap.** The Sunday branch has an `if start >= 14:00 → ettermiddag`
   with no `else`, so a Sunday shift that crosses midnight and starts *before*
   14:00 (e.g. 12:00–00:30) lands in `helgetimer` and in neither sub-bucket.
   Zero occurrences in R25/R26 today — latent, not a live wrong number.

The fix for both is one bucket decision, reusing the `is_night` flag already
computed at `shift_stats.py:161` (the same rule as `shift-classifier.js`):

```
nattevakt (crosses midnight, ends 04:00+)  → natt
starts 14:00+  OR  crosses midnight        → ettermiddag
otherwise                                  → dagtid
```

The `or crosses_midnight` clause is what closes the gap.

**Expect `helgetimer_ettermiddag` to drop** for most turnuser — night hours move
out of it. That is the point, and it is why Phase 4 is required, not optional.

---

## Phase 1 — `app/utils/shift_stats.py`

**1a.** Add the counter next to its siblings (~line 91):

```python
helgetimer_natt = 0
```

**1b.** Replace the whole `### WEEKENDS ###` block (lines ~170–220) with:

```python
                        ### WEEKENDS ###
                        # Each day computes its weekend hours; one shared
                        # decision then routes them into a bucket, so the
                        # three buckets always partition helgetimer.
                        helg_hours = 0
                        helg_start = start

                        if ukedag == 'Fredag':
                            fri_17 = start.replace(hour=17, minute=0, second=0)
                            if end > fri_17:
                                # Only the hours from 17:00 count, so that — not
                                # the shift's own start — decides the bucket.
                                helg_start = max(start, fri_17)
                                helg_hours = (end - helg_start).total_seconds() / 3600
                                helgedager += 1

                        elif ukedag == 'Lørdag':
                            helg_hours = (end - start).total_seconds() / 3600
                            helgedager += 1

                        elif ukedag == 'Søndag':
                            # Weekend window closes Monday 06:00. `end` is already
                            # +1 day when the shift crosses midnight, so min()
                            # handles both the crossing and non-crossing case.
                            mon_6am = start.replace(hour=6, minute=0, second=0) + pd.Timedelta(days=1)
                            helg_hours = (min(end, mon_6am) - start).total_seconds() / 3600
                            helgedager += 1

                        if helg_hours:
                            helgetimer += helg_hours
                            if is_night:
                                helgetimer_natt += helg_hours
                            elif helg_start.time() >= time(14, 0) or crosses_midnight:
                                helgetimer_ettermiddag += helg_hours
                            else:
                                helgetimer_dagtid += helg_hours
```

`is_night` and `crosses_midnight` are already in scope from lines 160–161.

**1c.** In `new_row` (~line 280), add the column and fix the rounding — the
existing `round(helgetimer_ettermiddag)` has no decimal place, unlike every
sibling:

```python
                'helgetimer_dagtid': [round(helgetimer_dagtid, 1)],
                'helgetimer_ettermiddag': [round(helgetimer_ettermiddag, 1)],
                'helgetimer_natt': [round(helgetimer_natt, 1)],
```

---

## Phase 2 — tests (write these before regenerating)

They should fail red against the current JSON. That is how you know Phase 3
worked.

**2a.** `tests/conftest.py:274` — let the helper place the shift on a chosen day:

```python
def single_shift_schedule(name, start, end, day=1):
    ...
            if w == 1 and d == day:
                week[str(d)] = {"ukedag": WEEKDAYS_NB[d - 1], "tid": [start, end], "dagsverk": "TEST"}
```

(The current body writes `week["1"]`; `week[str(d)]` generalises it. Day
numbers: Fredag = 5, Lørdag = 6, Søndag = 7.)

**2b.** `tests/test_shift_stats.py:183` — add the three sub-columns to
`_STAT_COLUMNS`:

```python
_STAT_COLUMNS = ["shift_cnt", "tidlig", "ettermiddag", "natt", "before_6",
                 "tidlig_6_8", "tidlig_8_12", "helgetimer",
                 "helgetimer_dagtid", "helgetimer_ettermiddag", "helgetimer_natt",
                 "longest_off_streak", "longest_work_streak", "avg_shift_hours"]
```

This list is what `test_stored_stats_match_fresh_computation` compares. It
currently omits every weekend sub-column, so **stale weekend data is invisible
to the suite today.** Adding them is what makes Phase 3 verifiable.

**2c.** Add the partition invariant — the test that would have caught the gap.
It belongs in the `TestStatsSanity` class (next to `test_helgetimer_non_negative`),
so it takes `self`:

```python
    def test_helg_buckets_partition_helgetimer(self, fresh_stats_r26):
        """dagtid + ettermiddag + natt must account for every weekend hour."""
        for _, row in fresh_stats_r26.iterrows():
            total = (row["helgetimer_dagtid"]
                     + row["helgetimer_ettermiddag"]
                     + row["helgetimer_natt"])
            # Four independent round(x, 1) calls (three buckets + the total),
            # so the rounded sum can drift up to 4 x 0.05 from the rounded
            # total. Observed worst case across R25+R26 is 0.1.
            assert abs(total - row["helgetimer"]) <= 0.2, (
                f"{row['turnus']}: buckets sum to {total}, helgetimer is {row['helgetimer']}"
            )
```

Until step 1c emits `helgetimer_natt`, this fails with `KeyError`, not an
assertion — that is the expected red.

**2d.** Boundary cases, in the style of the existing `_compute_natt` helpers
(write a `_compute_helg(start, end, day)` returning the three buckets):

| shift | expected |
|---|---|
| Lør 10:00–18:00 | dagtid |
| Lør 14:00–22:00 | ettermiddag |
| Søn 12:00–00:30 | ettermiddag (the gap) |
| Fre 22:00–06:00 | natt |
| Fre 10:00–19:00 | ettermiddag (2 h) — only the hours from 17:00 count, and they are evening hours regardless of when the shift began |
| Fre 15:00–20:00 | ettermiddag (3 h) — clipping check |
| Søn 22:00–08:00 | natt (8 h) — the window closes at Mon 06:00 |
| Fre 12:00–16:00 | no weekend hours at all |
| Ons 10:00–18:00 | no weekend hours at all |

---

## Phase 3 — regenerate the stats JSON

> **Do not run this until Phase 2 is fully green.** Regenerating makes
> `test_stored_stats_match_fresh_computation` pass by definition — it only
> compares stored against fresh, so a logic bug still in the code gets written
> into the JSON and the test turns green on top of it. The bucket tests in 2d
> are the only thing checking the logic itself.

```bash
venv/bin/python app/utils/shift_stats.py --all
venv/bin/pytest tests/test_shift_stats.py
```

`turnus_stats_R25.json` and `turnus_stats_R26.json` are **tracked in git**
(unlike the strekliste PNGs), so commit them and they travel with the deploy —
nothing to re-run on turnushjelper-1 or -2.

---

## Phase 4 — `/oversikt` (required)

The Helgeprofil stacked bar assumes two segments that sum to `helgetimer`.
After Phase 1 they no longer do.

| file | change |
|---|---|
| `app/routes/shifts/oversikt.py:26` | add `"helgetimer_natt"` to `metrics` |
| `app/static/js/modules/oversikt.js:435` | add `'helgetimer_natt'` to `HP_KEYS` |
| `oversikt.js:439` (`renderHelgeprofil`) | third dataset; relabel `'Kveld/natt (…)'` → `'Kveld'` |
| `app/templates/oversikt.html:307` | chart-title text, and the `dag vs kveld/natt` heading above it |
| `oversikt.js:38` (`HEATMAP_COLS`) | optional: a `helgetimer_natt` column + matching `<th>` |

---

## Phase 5 — the sorter

**5a. `app/routes/shifts/turnusliste.py:14`** — `SORT_METRICS` is the list of
stats columns copied into the `#turnus-metrics` JSON block. Add three:

```python
    "helgetimer",
    "helgetimer_dagtid",
    "helgetimer_ettermiddag",
    "helgetimer_natt",
```

**5b. `app/templates/components/sorter_controls.html`** — both the desktop
dropdown and the mobile modal render from `sorter_body()`, so write it once.
Move `helgetimer` out of `Belastning & fri` (line 66) into a new group:

```jinja
{% call sorter_group('Helg') %}
    {{ sorter_slider('helgetimer', 'Helgetimer', 'Færre', 'Flere', suffix) }}
    {{ sorter_slider('helgetimer-dagtid', 'Helg dagtid', 'Færre', 'Flere', suffix) }}
    {{ sorter_slider('helgetimer-ettermiddag', 'Helg kveld', 'Færre', 'Flere', suffix) }}
    {{ sorter_slider('helgetimer-natt', 'Helg natt', 'Færre', 'Flere', suffix) }}
{% endcall %}
```

The id is `helgetimer-ettermiddag` even though the label reads "Helg kveld":
every new base id is then the metric key with underscores swapped for hyphens,
which is what lets the JS derive it mechanically (see 5c). The Norwegian label
is a display concern and does not need to track the column name.

Placed third, between `Oppstart` and `Belastning & fri`.

Two rules the macro enforces implicitly:

- Base ids must be **kebab-case** — the macro builds `{base}-slider{suffix}`
  and `{base}-value{suffix}`, and the test regex only accepts `[a-z0-9-]`.
- **Do not rename `helgetimer`.** `initializeSorting()` gates the entire module
  on `#helgetimer-slider` existing (`sorting-system.js:25`); rename it and
  sorting dies silently, with no console error.

Update the comments at lines 9 and 50–51: 22 ids → 28, eleven criteria in three
families → fourteen in four.

No CSS change needed — `.filter-group` is generic, and a 4-item group fills the
2-column grid exactly.

**5c. `app/static/js/modules/sorting-system.js`** — every metric key is
hardcoded in five places. Miss one and you get a partial failure, not an error:

| line | add |
|---|---|
| 104 `calculateMinMax()` `criteria` | `'helgetimer_dagtid', 'helgetimer_ettermiddag', 'helgetimer_natt'` — without this, min/max falls back to `{min:0, max:1}` and values normalise off-scale |
| 166 `sortTurnuser()` `weights` | `helgetimer_dagtid: parseFloat(document.getElementById('helgetimer-dagtid-slider').value),` and the same for kveld / natt |
| 338 `getCriteriaLabel()` | `helgetimer_dagtid: 'Helg dagtid', helgetimer_ettermiddag: 'Helg kveld', helgetimer_natt: 'Helg natt',` |
| 376 `saveSortingSettings()` | the same three `getElementById(...).value` entries |
| 418 `applySavedSettings()` id chain | **required.** The fallback is `` `${key}-slider` ``, which yields `helgetimer_dagtid-slider` — an underscore that matches no element |

For 418, no new branches are needed — widen the fallback instead, so all three
new keys resolve on their own:

```javascript
                           `${key.replace(/_/g, '-')}-slider`;
```

The remaining ternary branches are the irregular ones whose id genuinely is not
derivable (`longest_off_streak` → `longest-off-slider`, `longest_work_streak`,
`kompdager_max`). The `shift_cnt` / `before_6` / `tidlig_6_8` / `tidlig_8_12`
branches are now redundant but harmless, and were left alone.

The metric key (snake_case, matches the stats column) and the DOM id (kebab)
are deliberately separate namespaces; that ternary chain is the only bridge.
Old `localStorage` entries simply lack the new keys, so those sliders start
at 0 — no migration needed.

**5d. `tests/test_turnusliste_sorter.py:52`** — `test_js_asks_for_the_eleven_known_sliders`
asserts the exact sorted id list and **will fail** until you add the three new
ids in alphabetical position (all three sort *before* `helgetimer-slider`).
Rename the test off "eleven".

The remaining tests read ids and metric keys out of the JS source, so they pick
up the additions on their own.

---

## Phase 6 — the stat grids

`mintur.html` (~line 224) showed only `helgetimer` and `helgetimer_dagtid`;
it now lists all four, and the "Helgtimer dag" typo is fixed to "Helg dagtid".

**Still open:** the same `.data-felt` grid on the turnus cards carries the same
two-of-four subset in `turnusliste.html:331` and `favorites.html:224`, with the
same typo. Those are the cards the new sliders reorder, so a user dragging
"Helg natt" cannot see the number they are sorting by. Adding two rows to each
is low-risk but changes the grid's height on every card, so it was left as a
deliberate decision rather than folded in.

---

## Verify

```bash
venv/bin/pytest tests/test_shift_stats.py tests/test_turnusliste_sorter.py
venv/bin/pytest
```

Then load `/turnusliste`: four groups in the Sorter panel, the count badge
reaching 2–3 as you drag, and the mobile modal showing the same four groups.
On `/oversikt`, confirm the Helgeprofil bars still reach the same total height
per turnus — three segments now instead of two.
