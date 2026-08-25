"""Tests for app/services/roster_export_service.py.

The builder is pure — innplassering records, schedule dict and date index all
come in as arguments — so these tests need neither the database nor the
gitignored turnusdata/ tree. The R26 test at the bottom skips without them.
"""

import datetime
import os

import pytest

from app.services import roster_export_service as res
from app.utils import turnuskalender as tk


def _schedule():
    """One tur, week 4 day 3 = the 1413 anchor, week 1 day 1 = a fri day."""
    return {
        "OSL_10_Østre_Linje": {
            "4": {
                "3": {"dagsverk": "1413", "start": "6:05", "slutt": "15:00",
                      "tid": ["6:05", "15:00"]},
            },
            "1": {
                "1": {"dagsverk": "", "start": ["X"], "slutt": "", "tid": ["X"]},
                "2": {"dagsverk": "", "start": [], "slutt": "", "tid": []},
            },
        }
    }


MONDAY = datetime.date(2026, 1, 5)


def _index(group, day, date):
    return {date: (group, day)}


class TestBuildRows:
    def test_resolves_a_dagsverk(self):
        # linje 1 in group 3 -> rotation week ((3 + 1 - 1) % 6) + 1 = 4
        assert tk.rotation_week(3, 1) == 4
        rows = res.build_rows(
            [{"rullenummer": "97089", "shift_title": "OSL_10_Østre_Linje",
              "linjenummer": 1, "is_7th_driver": 0}],
            _schedule(),
            _index(3, 2, MONDAY),
        )["rader"]
        assert rows == [{
            "rullenummer": "97089",
            "dato": "2026-01-05",
            "dv_nummer": "1413",
            "start": "6:05",
            "slutt": "15:00",
            "tur": "OSL_10_Østre_Linje",
            "rotasjonsuke": 4,
            "linjenummer": 1,
            "er_7_forer": 0,
            "fri_kode": None,
        }]

    def test_fri_day_keeps_its_code_and_has_no_dagsverk(self):
        rows = res.build_rows(
            [{"rullenummer": "1", "shift_title": "OSL_10_Østre_Linje",
              "linjenummer": 1, "is_7th_driver": 0}],
            _schedule(),
            _index(0, 0, MONDAY),
        )["rader"]
        assert rows[0]["dv_nummer"] is None
        assert rows[0]["fri_kode"] == "X"

    def test_blank_day_has_neither_dagsverk_nor_code(self):
        """The sleep-off day after a night shift is blank, not a fri code."""
        rows = res.build_rows(
            [{"rullenummer": "1", "shift_title": "OSL_10_Østre_Linje",
              "linjenummer": 1, "is_7th_driver": 0}],
            _schedule(),
            _index(0, 1, MONDAY),
        )["rader"]
        assert rows[0]["dv_nummer"] is None
        assert rows[0]["fri_kode"] is None

    def test_seventh_driver_is_flagged(self):
        rows = res.build_rows(
            [{"rullenummer": "64895", "shift_title": "OSL_10_Østre_Linje",
              "linjenummer": 1, "is_7th_driver": 1}],
            _schedule(),
            _index(3, 2, MONDAY),
        )["rader"]
        assert rows[0]["er_7_forer"] == 1

    def test_missing_linjenummer_is_reported_not_guessed(self):
        result = res.build_rows(
            [{"rullenummer": "1", "shift_title": "OSL_10_Østre_Linje",
              "linjenummer": None, "is_7th_driver": 0}],
            _schedule(),
            _index(3, 2, MONDAY),
        )
        assert result["rader"] == []
        assert result["hoppet_over"] == [("1", "mangler linjenummer")]

    def test_unknown_tur_is_reported_not_guessed(self):
        result = res.build_rows(
            [{"rullenummer": "1", "shift_title": "OSL_99", "linjenummer": 1,
              "is_7th_driver": 0}],
            _schedule(),
            _index(3, 2, MONDAY),
        )
        assert result["rader"] == []
        assert result["hoppet_over"] == [("1", "ukjent tur OSL_99")]

    def test_one_row_per_driver_per_date(self):
        index = {MONDAY: (3, 2), MONDAY + datetime.timedelta(days=1): (3, 2)}
        rows = res.build_rows(
            [{"rullenummer": "1", "shift_title": "OSL_10_Østre_Linje",
              "linjenummer": 1, "is_7th_driver": 0},
             {"rullenummer": "2", "shift_title": "OSL_10_Østre_Linje",
              "linjenummer": 1, "is_7th_driver": 0}],
            _schedule(),
            index,
        )["rader"]
        assert len(rows) == 4
        assert {r["rullenummer"] for r in rows} == {"1", "2"}

    def test_rows_are_sorted_by_rullenummer_then_date(self):
        index = {MONDAY + datetime.timedelta(days=1): (3, 2), MONDAY: (3, 2)}
        rows = res.build_rows(
            [{"rullenummer": "2", "shift_title": "OSL_10_Østre_Linje",
              "linjenummer": 1, "is_7th_driver": 0},
             {"rullenummer": "1", "shift_title": "OSL_10_Østre_Linje",
              "linjenummer": 1, "is_7th_driver": 0}],
            _schedule(),
            index,
        )["rader"]
        assert [(r["rullenummer"], r["dato"]) for r in rows] == [
            ("1", "2026-01-05"), ("1", "2026-01-06"),
            ("2", "2026-01-05"), ("2", "2026-01-06"),
        ]


@pytest.mark.skipif(
    not os.path.exists(tk.nokkel_path("R26")),
    reason="turnusdata/r26 is gitignored and not present",
)
class TestAgainstRealR26:
    def test_the_1413_anchor_lands_on_a_wednesday(self):
        """Rotation week 4 day 3 of OSL_10 is a Wednesday, and every date the
        nøkkel puts there must carry dagsverk 1413."""
        import json

        from config import AppConfig

        index = tk.build_date_index("R26")
        schedule = {}
        path = os.path.join(
            AppConfig.turnusfiler_dir, "r26", "turnus_schedule_R26.json"
        )
        for entry in json.load(open(path, encoding="utf-8")):
            schedule.update(entry)

        rows = res.build_rows(
            [{"rullenummer": "test", "shift_title": "OSL_10_Østre_Linje",
              "linjenummer": 1, "is_7th_driver": 0}],
            schedule,
            index,
        )["rader"]

        treff = [r for r in rows if r["dv_nummer"] == "1413"]
        assert treff, "1413 never resolved"
        for r in treff:
            assert datetime.date.fromisoformat(r["dato"]).weekday() == 2
            assert r["rotasjonsuke"] == 4
            assert (r["start"], r["slutt"]) == ("6:05", "15:00")
