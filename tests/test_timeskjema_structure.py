"""Structural invariants for every committed Timeskjema export.

These files come from NLF and their shape is outside our control, so this module
pins what must hold for *any* rutetermin rather than what happens to be true of
one. Nothing here asserts a count: the number of turnuser changes every year, and
a test that had to be edited each December would just be edited without thought.

Complements, and deliberately does not duplicate, `TestGoldenRealFile` in
`tests/test_timeskjema_parser.py`, which pins R26's specific values (57 turnuser,
hand-verified spot cells, rutetermin dates).

New exports are picked up automatically: any `turnusdata/*/*.xls` is
parametrized in. `scripts/probe_timeskjema.py` diffs an incoming file against
these; this module is what guards the baseline they are diffed against.

Note on overlap: the parser enforces several of these invariants itself, so
those tests would fail alongside `test_parses` rather than alone. They earn
their place two other ways — they name the specific violation instead of
leaving a generic parse error, and they fail if the *parser* is ever loosened,
which nothing else here would catch.
"""

import functools
import glob
import os

import pytest

from app.utils.pdf.scraper_validator import validate_turnus_json
from app.utils.timeskjema_parser import (
    _FREE_NORMALIZE,
    _NON_ASCII_WEEKDAYS,
    WEEKDAYS,
    _clean,
    _count_weekday_rows,
    parse_timeskjema,
    sniff_format,
)
from config import AppConfig

# Not every .xls under turnusdata is necessarily a timeskjema, so classify by
# content rather than trusting the extension — `sniff_format` refuses to guess
# (real OLE2 Excel, HTML and PDF all come back 'unknown'). Note that turnusnøkkel
# files are .xlsx and never match this glob in the first place.
_XLS_FILES = sorted(glob.glob(os.path.join(AppConfig.turnusfiler_dir, "*", "*.xls")))


def _sniffed(path):
    with open(path, "rb") as f:
        return sniff_format(f.read())


_EXPORTS = [p for p in _XLS_FILES if _sniffed(p) == "timeskjema"]
_UNRECOGNISED = [p for p in _XLS_FILES if p not in _EXPORTS]


@functools.lru_cache(maxsize=None)
def _parsed(path):
    return parse_timeskjema(path)


@functools.lru_cache(maxsize=None)
def _raw(path):
    with open(path, "rb") as f:
        return f.read()


def _turnuser(path):
    return {name: data for entry in _parsed(path).turnuser for name, data in entry.items()}


@functools.lru_cache(maxsize=None)
def _raw_off_codes(path):
    """Dv.Nr. values on day rows with no start/end time, read straight from the
    file — i.e. whatever NLF used to mark a fridag, before normalization."""
    codes = set()
    header = None
    for line in _raw(path).decode("iso-8859-1").split("\n"):
        cells = [_clean(c) for c in line.split("\t")]
        if cells[0] == "Dag":
            header = cells
        elif header and cells[0] in WEEKDAYS:
            dv, start, end = (
                _cell(cells, header.index("Dv.Nr.")),
                _cell(cells, header.index("Start tid")),
                _cell(cells, header.index("Avslutningstid")),
            )
            if dv and not start and not end:
                codes.add(dv)
    return frozenset(codes)


def _cell(row, index):
    return row[index] if index < len(row) else ""


@pytest.mark.parametrize(
    "path", _UNRECOGNISED, ids=[os.path.basename(p) for p in _UNRECOGNISED]
)
def test_no_unrecognised_xls_in_turnusdata(path):
    """Fail rather than filter silently.

    Content-classifying the glob would otherwise fail open: an export corrupted
    into real Excel — by opening and saving it in a spreadsheet program, the most
    likely accident — sniffs as 'unknown', drops out of _EXPORTS, and every
    invariant below would pass by simply not running.
    """
    pytest.fail(
        f"{os.path.basename(path)} is not a timeskjema export "
        f"(sniff_format: {_sniffed(path)!r}). Either it was re-saved as real "
        "Excel and must be restored from the original NLF export, or it does not "
        "belong under turnusdata/."
    )


# Applied to the class, not the module: an unrecognised file must still be
# reported when it is the *only* .xls present.
@pytest.mark.skipif(
    not _EXPORTS,
    reason=f"No timeskjema exports found under {AppConfig.turnusfiler_dir}",
)
@pytest.mark.parametrize("path", _EXPORTS, ids=[os.path.basename(p) for p in _EXPORTS])
class TestCommittedExportStructure:
    def test_parses(self, path):
        assert _parsed(path).turnuser, "no turnuser parsed"

    def test_validator_passes(self, path):
        valid, errors = validate_turnus_json(_parsed(path).turnuser)
        assert valid, errors

    def test_is_iso8859_1_not_utf8(self, path):
        # The parser hardcodes an iso-8859-1 decode. A UTF-8 export would drop
        # Lørdag/Søndag rows and be refused on import, so the committed baseline
        # must genuinely be latin-1 — see _diagnose_encoding.
        with pytest.raises(UnicodeDecodeError):
            _raw(path).decode("utf-8")

    def test_weekend_labels_survive_the_decode(self, path):
        # The two non-ASCII weekday labels are the only ones that prove the
        # encoding is right; Mandag..Fredag match under any decode.
        text = _raw(path).decode("iso-8859-1")
        assert _count_weekday_rows(text, _NON_ASCII_WEEKDAYS) > 0

    def test_every_turnus_is_a_complete_6x7_rotation(self, path):
        # 42 day cells is hardcoded in the parser, the validator and
        # kompdag_utils; a rutetermin that broke it would be a code change.
        for name, turnus in _turnuser(path).items():
            for uke in range(1, 7):
                assert uke in turnus, f"{name}: missing uke {uke}"
                for dag in range(1, 8):
                    assert dag in turnus[uke], f"{name}: missing uke {uke} dag {dag}"

    def test_off_codes_stay_within_free_normalize(self, path):
        # Scanned from the raw file rather than from parsed output: _parse_day
        # maps every accepted code into {X, O, T}, so asserting against parsed
        # output could never fail. A new code does fail the parse, but with a
        # generic "inconsistent values" message — this names the code instead.
        # Kompdag counting keys off exactly X/O/T (overenskomsten §5.13.1).
        seen = _raw_off_codes(path)
        unknown = seen - set(_FREE_NORMALIZE)
        assert not unknown, f"off-codes not in _FREE_NORMALIZE: {sorted(unknown)}"

    def test_single_column_layout(self, path):
        # Every block must share one header; a per-block layout would mean the
        # export format changed mid-file.
        layouts = set()
        for line in _raw(path).decode("iso-8859-1").split("\n"):
            cells = [_clean(c) for c in line.split("\t")]
            if cells[0] == "Dag":
                layouts.add(tuple(c for c in cells if c))
        assert len(layouts) == 1, f"{len(layouts)} different column layouts"

    def test_hours_totals_present(self, path):
        for name, turnus in _turnuser(path).items():
            assert turnus["kl_timer"], f"{name}: empty kl_timer"
            assert turnus["tj_timer"], f"{name}: empty tj_timer"

    def test_rutetermin_spans_roughly_a_year(self, path):
        result = _parsed(path)
        assert result.rutetermin_start and result.rutetermin_end
        days = (result.rutetermin_end - result.rutetermin_start).days
        # A rutetermin runs December to December, so it crosses two calendar
        # years — which is why kompdag holidays are unioned across both.
        assert 360 <= days <= 371, f"rutetermin spans {days} days"
        assert result.rutetermin_end.year == result.rutetermin_start.year + 1
