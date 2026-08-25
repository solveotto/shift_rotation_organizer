"""The turnusnøkkel grid: which calendar date falls in which rotation cell.

The schedule JSON is an abstract 6-week rotation carrying no dates at all, so
``turnusnøkkel_{YEAR}_org.xlsx`` is the project's only calendar-date source.
Sheet "Turnusnøkkel" holds 6 nøkkel groups of 8 rows each (one header row then
seven weekday rows, Monday first), with dates in columns H-P — nine columns,
one for each time that group comes round in the rutetermin.

A worker on linje ``j`` follows rotation week ``((g + j - 1) % 6) + 1`` while
the calendar is in group ``g``. That one line is the whole mapping, and it used
to live inline in mintur. It is here so the /mintur page and the roster export
cannot drift apart about which dagsverk a driver has on a date — they are the
same question asked by two callers.

``kompdag_utils.get_holiday_positions`` walks the identical grid and is the
obvious next caller, but its counts are calibrated and test-asserted, so it is
deliberately left alone rather than migrated as a side effect of this change.
"""

import logging
import os

from config import AppConfig

logger = logging.getLogger(__name__)

SHEET_NAME = "Turnusnøkkel"
NOKKEL_GROUPS = 6
ROWS_PER_GROUP = 8
DAYS_PER_WEEK = 7
#: Columns H-P, zero-based and end-exclusive — the nine week columns per group.
DATE_COLUMNS = slice(7, 16)
#: The grid occupies the first 48 rows: 6 groups x 8 rows.
GRID_ROWS = NOKKEL_GROUPS * ROWS_PER_GROUP


def nokkel_path(year_identifier) -> str:
    """Path to a year's nøkkel template. The file may not exist."""
    return os.path.join(
        AppConfig.turnusfiler_dir,
        str(year_identifier).lower(),
        f"turnusnøkkel_{year_identifier}_org.xlsx",
    )


def schedule_path(year_identifier) -> str:
    """Conventional path to a year's rotation schedule JSON.

    ``TurnusSet`` rows store absolute paths that go stale whenever the data
    store moves, so callers should prefer the stored path only when it exists
    and fall back here — the same rule ``DataframeManager`` follows.
    """
    return os.path.join(
        AppConfig.turnusfiler_dir,
        str(year_identifier).lower(),
        f"turnus_schedule_{year_identifier}.json",
    )


def load_nokkel_rows(year_identifier):
    """Read the grid rows from the nøkkel template.

    Returns a list of openpyxl cell rows, or ``None`` when the template is
    missing — callers must be able to tell "no template" from "no dates in it",
    the same distinction ``count_kompdager`` relies on.
    """
    import openpyxl

    path = nokkel_path(year_identifier)
    if not os.path.exists(path):
        logger.warning("Turnusnøkkel template not found: %s", path)
        return None

    workbook = openpyxl.load_workbook(path, data_only=True)
    try:
        rows = [list(row) for row in
                workbook[SHEET_NAME].iter_rows(min_row=1, max_row=GRID_ROWS)]
    finally:
        workbook.close()
    return rows


def cell_date(cell):
    """The date in a cell, or None. Openpyxl hands back datetimes, not dates."""
    value = getattr(cell, "value", None)
    if value is None or not hasattr(value, "strftime"):
        return None
    return value.date() if hasattr(value, "date") else value


def build_date_index(year_identifier=None, *, rows=None):
    """``{date: (group, day)}`` — group 0-5, day 0-6 with Monday as 0.

    Pass ``rows`` to work on an already-loaded grid; otherwise the year's
    template is read. Returns ``{}`` when the template is missing.
    """
    if rows is None:
        rows = load_nokkel_rows(year_identifier)
    if not rows:
        return {}

    index = {}
    for group in range(NOKKEL_GROUPS):
        for day in range(DAYS_PER_WEEK):
            row = rows[group * ROWS_PER_GROUP + 1 + day]
            for cell in row[DATE_COLUMNS]:
                date = cell_date(cell)
                if date is not None:
                    index[date] = (group, day)
    return index


def week_labels(rows, group):
    """The "Uke NN" labels across one group's header row."""
    header = rows[group * ROWS_PER_GROUP]
    return [str(c.value) for c in header[DATE_COLUMNS] if c.value is not None]


def rotation_week(group, linjenummer) -> int:
    """Which of the rotation's 6 weeks linje ``linjenummer`` is in, in ``group``.

    ``group`` is 0-based as ``build_date_index`` reports it; ``linjenummer`` is
    the 1-6 position within the tur, as ``Innplassering`` stores it.
    """
    return (group + linjenummer - 1) % NOKKEL_GROUPS + 1


def lookup_cell(turnus_weeks, week, day):
    """One cell of a tur's rotation, or None.

    ``turnus_weeks`` is the schedule JSON's value for one tur: weeks keyed
    "1".."6", each holding days keyed "1".."7". ``week`` is 1-based as
    ``rotation_week`` returns it; ``day`` is **0-based**, as
    ``build_date_index`` reports it — the +1 happens here so no caller has to
    remember which of the two conventions it is holding.
    """
    cell = (turnus_weeks or {}).get(str(week), {})
    if not isinstance(cell, dict):
        return None
    cell = cell.get(str(day + 1))
    return cell if isinstance(cell, dict) else None
