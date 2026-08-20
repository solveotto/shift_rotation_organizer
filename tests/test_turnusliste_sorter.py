"""Guards the slider ids shared by the sorter markup and sorting-system.js.

The panel renders from one Jinja macro (components/sorter_controls.html) but the
JS reaches every slider by literal id — sortTurnuser(), saveSortingSettings()
and applySavedSettings() all do unguarded document.getElementById(...).value,
and initializeSorting() gates the whole module on #helgetimer-slider existing.
A renamed or mistyped macro argument therefore kills sorting silently, with no
console error until a user drags something.

So rather than restate a list here, these tests read the ids the JS actually
asks for and assert the page renders each one, in both the desktop and the
-mobile variant.
"""

import json
import re
from pathlib import Path

import pandas as pd

from app.models import TurnusSet
from tests.conftest import login_user

SORTING_JS = (
    Path(__file__).resolve().parent.parent
    / "app"
    / "static"
    / "js"
    / "modules"
    / "sorting-system.js"
)


def _slider_ids_required_by_js():
    """Every '<name>-slider' id sorting-system.js looks up by hand."""
    source = SORTING_JS.read_text(encoding="utf-8")
    ids = set(re.findall(r"getElementById\(\s*'([a-z0-9-]+-slider)'\s*\)", source))
    ids.update(re.findall(r"querySelector\(\s*'#([a-z0-9-]+-slider)'\s*\)", source))
    return sorted(ids)


def _render_turnusliste(client, sample_user, db_session):
    db_session.add(TurnusSet(name="R26", year_identifier="R26", is_active=1))
    db_session.commit()
    login_user(client, sample_user["username"], sample_user["password"])

    resp = client.get("/turnusliste")
    assert resp.status_code == 200
    return resp.get_data(as_text=True)


def test_js_asks_for_the_fourteen_known_sliders():
    """Fails if a criterion is added to the JS without extending the macro."""
    assert _slider_ids_required_by_js() == [
        "before-6-slider",
        "ettermiddag-slider",
        "helgetimer-dagtid-slider",
        "helgetimer-ettermiddag-slider",
        "helgetimer-natt-slider",
        "helgetimer-slider",
        "kompdager-slider",
        "longest-off-slider",
        "longest-streak-slider",
        "natt-slider",
        "shift-cnt-slider",
        "tidlig-6-8-slider",
        "tidlig-8-12-slider",
        "tidlig-slider",
    ]


def test_every_slider_the_js_needs_renders(client, sample_user, db_session):
    html = _render_turnusliste(client, sample_user, db_session)

    for slider_id in _slider_ids_required_by_js():
        # Desktop dropdown and mobile modal, plus the value chip
        # updateSliderValue() derives by replacing '-slider' with '-value'.
        assert f'id="{slider_id}"' in html, f"missing desktop slider {slider_id}"
        assert f'id="{slider_id}-mobile"' in html, f"missing mobile slider {slider_id}"
        value_id = slider_id.replace("-slider", "-value")
        assert f'id="{value_id}"' in html, f"missing value chip {value_id}"
        assert f'id="{value_id}-mobile"' in html, f"missing chip {value_id}-mobile"


def test_sliders_are_labelled(client, sample_user, db_session):
    """Every range input needs a <label for> — screen readers announce nothing
    without it, which is the state the panel shipped in before this."""
    html = _render_turnusliste(client, sample_user, db_session)

    for slider_id in _slider_ids_required_by_js():
        for full_id in (slider_id, f"{slider_id}-mobile"):
            assert f'for="{full_id}"' in html, f"unlabelled slider {full_id}"


def test_reset_and_done_controls_render(client, sample_user, db_session):
    html = _render_turnusliste(client, sample_user, db_session)

    assert 'id="reset-sorting"' in html
    assert 'id="reset-sorting-mobile"' in html
    # Ferdig closes the dropdown from JS; data-bs-toggle would be a no-op here.
    assert 'id="sorter-done"' in html
    assert 'data-bs-auto-close="outside"' in html


# ---------------------------------------------------------------------------
# #turnus-metrics — the numeric data the sorter ranks on
#
# sorting-system.js used to read these values back out of the rendered
# .data-felt grid, by positional <b> index and through parseInt. That truncated
# helgetimer 58.3 to 58, turned an unknown kompdager count ("–") into 0 — the
# best rank under "Færre" — and would silently mis-map every field after any
# cell that moved in the grid. The route now ships real numbers instead.
# ---------------------------------------------------------------------------

FAKE_TURNUSER = ("OSL_01", "OSL_02", "OSL_03")


def _metric_keys_required_by_js():
    """Every metric name sorting-system.js expects inside #turnus-metrics.

    Two hardcoded lists in the JS must agree with what the route emits: the
    `criteria` array in calculateMinMax() and the keys of the `weights` object
    in sortTurnuser(). They can drift from the data and from each other, so
    both are read rather than restated here.
    """
    source = SORTING_JS.read_text(encoding="utf-8")

    criteria = re.search(r"const criteria = \[(.*?)\]", source, re.S)
    assert criteria, "calculateMinMax() no longer declares `const criteria = [...]`"
    keys = set(re.findall(r"'([a-z0-9_]+)'", criteria.group(1)))

    weights = re.search(r"const weights = \{(.*?)\};", source, re.S)
    assert weights, "sortTurnuser() no longer declares `const weights = {...}`"
    keys.update(re.findall(r"([a-z0-9_]+):", weights.group(1)))

    return keys


def _stats_row(**overrides):
    """One row of turnus_stats_{ID}.json, with the columns the sorter uses."""
    row = {
        "shift_cnt": 25,
        "tidlig": 11,
        "ettermiddag": 6,
        "natt": 8,
        "before_6": 1,
        "tidlig_6_8": 8,
        "tidlig_8_12": 2,
        "helgetimer": 58.3,
        "helgetimer_dagtid": 17.5,
        "helgetimer_ettermiddag": 15.6,
        "helgetimer_natt": 25.2,
        "longest_off_streak": 5,
        "longest_work_streak": 7,
    }
    row.update(overrides)
    return row


def _install_fake_turnus_data(monkeypatch, stats, komp):
    """Stand in for the committed R26 files.

    Deterministic beats real here: the float and null cases have to hold exact
    values. OSL_03 is deliberately absent from the stats frame — the template
    loops over turnus_data, so it still renders a card, and the metrics block
    must still carry an entry for it or that card sits still while the rest of
    the list reorders around it.
    """
    turnus_data = [
        {
            name: {
                "1": {
                    "1": {
                        "ukedag": "Mandag",
                        "tid": ["06:00", "14:00"],
                        "start": "06:00",
                        "slutt": "14:00",
                        "dagsverk": f"100{index}_TEST",
                    }
                },
                "kl_timer": "150:00",
                "tj_timer": "160:00",
            }
        }
        for index, name in enumerate(FAKE_TURNUSER)
    ]
    df = pd.DataFrame([dict(row, turnus=name) for name, row in stats.items()])

    class FakeDataframeManager:
        def __init__(self, turnus_set_id=None):
            self.df = df
            self.turnus_data = turnus_data

    # The route does `from app.utils import df_utils`, so this is the very same
    # module object it reaches through — not scoped isolation, but monkeypatch
    # restores it afterwards.
    monkeypatch.setattr("app.utils.df_utils.DataframeManager", FakeDataframeManager)
    # count_kompdager is imported by name into the route: a real use-site patch.
    monkeypatch.setattr(
        "app.routes.shifts.turnusliste.count_kompdager", lambda _id: komp
    )


def _render_with_fakes(
    client, sample_user, db_session, monkeypatch, stats=None, komp=None
):
    if stats is None:
        stats = {
            "OSL_01": _stats_row(),
            "OSL_02": _stats_row(helgetimer=58.9, natt=0),
        }
    _install_fake_turnus_data(monkeypatch, stats, komp)
    return _render_turnusliste(client, sample_user, db_session)


def _metrics_block(html):
    """Parse #turnus-metrics the way JSON.parse would.

    Python's json module accepts bare NaN/Infinity; JSON.parse rejects them and
    takes the whole sorter down with it. parse_constant makes the test fail
    where the browser would.
    """
    match = re.search(
        r'<script id="turnus-metrics" type="application/json">(.*?)</script>',
        html,
        re.S,
    )
    assert match, "#turnus-metrics block missing"

    def reject(value):
        raise AssertionError(f"{value} is not valid JSON — JSON.parse would throw")

    return json.loads(match.group(1), parse_constant=reject)


def test_metrics_block_has_one_entry_per_rendered_card(
    client, sample_user, db_session, monkeypatch
):
    html = _render_with_fakes(client, sample_user, db_session, monkeypatch)
    metrics = _metrics_block(html)

    cards = re.findall(r'<li data-turnus="([^"]+)"', html)
    assert sorted(cards) == sorted(FAKE_TURNUSER)
    assert sorted(metrics) == sorted(FAKE_TURNUSER)

    # OSL_03 has no stats row: present, but every criterion unknown. Not zeroes,
    # which would rank it best on every "Færre" slider.
    assert set(metrics["OSL_03"].values()) == {None}


def test_every_metric_the_js_reads_is_present(
    client, sample_user, db_session, monkeypatch
):
    """Fails if a criterion is added to the JS without the route supplying it."""
    html = _render_with_fakes(client, sample_user, db_session, monkeypatch)
    metrics = _metrics_block(html)

    required = _metric_keys_required_by_js()
    assert required, "regex found no metric names in sorting-system.js"

    for name, entry in metrics.items():
        missing = required - set(entry)
        assert not missing, f"{name} is missing {sorted(missing)}"


def test_data_turnus_carries_the_raw_name_exactly_once(
    client, sample_user, db_session, monkeypatch
):
    """The attribute is the sorter's identity, and .t-name cannot serve.

    .t-name goes through the display_name filter, so it reads "OSL 01" while
    the metrics are keyed "OSL_01". The attribute must also stay unique per
    card: turnusliste.js resolves the ?turnus= highlight with a page-wide
    querySelector, so a second element carrying it would shadow the <li>.
    """
    html = _render_with_fakes(client, sample_user, db_session, monkeypatch)

    assert 'data-turnus="OSL_01"' in html
    assert "OSL 01" in html  # what the user actually sees
    assert html.count('data-turnus="OSL_01"') == 1
    assert len(re.findall(r'data-turnus="', html)) == len(FAKE_TURNUSER)


def test_float_metrics_keep_their_decimals(
    client, sample_user, db_session, monkeypatch
):
    """helgetimer is the only float among the sorted criteria — and the slider
    people actually use. parseInt used to drop the decimals, manufacturing ties
    between turnuser that differ."""
    html = _render_with_fakes(client, sample_user, db_session, monkeypatch)
    metrics = _metrics_block(html)

    assert metrics["OSL_01"]["helgetimer"] == 58.3
    assert metrics["OSL_02"]["helgetimer"] == 58.9


def test_unknown_kompdager_is_null_not_zero(
    client, sample_user, db_session, monkeypatch
):
    """count_kompdager returns None when the nøkkel template is unavailable."""
    html = _render_with_fakes(client, sample_user, db_session, monkeypatch, komp=None)
    metrics = _metrics_block(html)

    assert metrics["OSL_01"]["kompdager_max"] is None
    assert "<b>–</b>" in html  # the display label is still an en-dash


def test_known_kompdager_is_the_bare_count(
    client, sample_user, db_session, monkeypatch
):
    """The grid shows "4 (L1)"; the sorter needs the number behind it."""
    html = _render_with_fakes(
        client,
        sample_user,
        db_session,
        monkeypatch,
        komp={"OSL_01": [4, 1, 3, 2, 2, 4], "OSL_02": [0, 0, 0, 0, 0, 0]},
    )
    metrics = _metrics_block(html)

    assert metrics["OSL_01"]["kompdager_max"] == 4
    assert "4 (L1)" in html
    # A genuine zero is a count, not a missing value.
    assert metrics["OSL_02"]["kompdager_max"] == 0
    assert metrics["OSL_03"]["kompdager_max"] is None


def test_non_finite_values_become_null(client, sample_user, db_session, monkeypatch):
    """json.dumps writes a bare NaN, which JSON.parse refuses — one such cell
    would take the entire sorter offline. No committed stats file has one, so
    only this test covers it."""
    html = _render_with_fakes(
        client,
        sample_user,
        db_session,
        monkeypatch,
        stats={
            "OSL_01": _stats_row(helgetimer=float("nan")),
            "OSL_02": _stats_row(),
        },
    )
    metrics = _metrics_block(html)  # parse_constant fails the test if NaN leaked

    assert metrics["OSL_01"]["helgetimer"] is None
    assert metrics["OSL_02"]["helgetimer"] == 58.3
