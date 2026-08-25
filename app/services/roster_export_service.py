"""Export the planned roster: which rullenummer works which dagsverk, by date.

Three sources meet here, and none of them alone answers the question:

  Innplassering        rullenummer -> (tur, linjenummer)
  turnusnøkkel         date        -> (nøkkel group, weekday)
  turnus_schedule JSON (tur, rotation week, weekday) -> dagsverk

``rotation_week(group, linjenummer)`` closes the loop. The result is a flat
file consumed by the sibling nlfstreik app, which holds the same drivers by
NLF medlemsnummer and needs to know what a striking driver was rostered to do
on a date when no duty screenshot exists.

One caveat travels with the data. The innplassering PDF places a 7.fører at a
linje that a regular driver already holds, so both come out on the same dagsverk
on the same date — 1 692 such pairs across R26, on top of 5 922 where several
drivers share a Ramme reserve span. ``er_7_forer`` is exported so the consumer
can decide; nothing here tries to resolve it, because which of the two actually
works the duty is not in any of these three sources.

``build_rows`` is pure — records, schedule and date index all arrive as
arguments — so the join is testable without a database or the gitignored
turnusdata/ tree. Only ``export`` touches the filesystem.

Payload keys are Norwegian because they are column names in the consuming app,
which is Norwegian throughout; the code around them stays English, as here.
"""

import datetime
import gzip
import hashlib
import json
import logging
import os

from app.utils import turnuskalender

logger = logging.getLogger(__name__)

#: A rostered day off. Anything else in the cell's ``tid`` is a clock time.
#: A cell with no ``tid`` at all is the sleep-off half of a night shift — blank,
#: which is not the same as a fri code and must not be reported as one.
FRI_CODES = frozenset({"X", "O", "T"})


def _fri_code(cell):
    tid = cell.get("tid") or []
    first = tid[0] if tid else None
    return first if first in FRI_CODES else None


def build_rows(innplassering, schedule, date_index):
    """Join the three sources into one row per (rullenummer, date).

    ``innplassering`` is a list of dicts with ``rullenummer``, ``shift_title``,
    ``linjenummer`` and ``is_7th_driver``. Returns
    ``{"rader": [...], "hoppet_over": [(rullenummer, reason), ...]}``.

    A driver whose tur or linjenummer cannot be resolved is **reported, never
    guessed at**: a wrong dagsverk here becomes a wrong list of cancelled
    trains at the far end.
    """
    rows = []
    skipped = []
    dates = sorted(date_index)

    for record in sorted(innplassering, key=lambda r: str(r["rullenummer"])):
        rullenummer = str(record["rullenummer"])
        tur = record["shift_title"]
        linjenummer = record.get("linjenummer")

        if not linjenummer:
            skipped.append((rullenummer, "mangler linjenummer"))
            continue
        weeks = schedule.get(tur)
        if weeks is None:
            skipped.append((rullenummer, f"ukjent tur {tur}"))
            continue

        for date in dates:
            group, day = date_index[date]
            week = turnuskalender.rotation_week(group, linjenummer)
            cell = turnuskalender.lookup_cell(weeks, week, day)
            if cell is None:
                continue
            dagsverk = cell.get("dagsverk") or None
            rows.append({
                "rullenummer": rullenummer,
                "dato": date.isoformat(),
                "dv_nummer": dagsverk,
                "start": cell.get("start") if dagsverk else None,
                "slutt": cell.get("slutt") if dagsverk else None,
                "tur": tur,
                "rotasjonsuke": week,
                "linjenummer": linjenummer,
                "er_7_forer": 1 if record.get("is_7th_driver") else 0,
                "fri_kode": None if dagsverk else _fri_code(cell),
            })

    return {"rader": rows, "hoppet_over": skipped}


def _md5(path):
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_schedule(path):
    """Flatten the schedule JSON's list-of-single-key-dicts into one dict."""
    schedule = {}
    with open(path, encoding="utf-8") as handle:
        for entry in json.load(handle):
            schedule.update(entry)
    return schedule


def export(year_identifier, schedule_path, innplassering, stasjonering="OSL",
           out_path=None):
    """Build the payload and, when ``out_path`` is given, write it gzipped."""
    date_index = turnuskalender.build_date_index(year_identifier)
    if not date_index:
        raise FileNotFoundError(
            f"Turnusnøkkel missing for {year_identifier}: "
            f"{turnuskalender.nokkel_path(year_identifier)}"
        )

    schedule = load_schedule(schedule_path)
    built = build_rows(innplassering, schedule, date_index)

    payload = {
        "kode": year_identifier,
        "stasjonering": stasjonering,
        "fra": min(date_index).isoformat(),
        "til": max(date_index).isoformat(),
        "kilde": {
            "schedule_md5": _md5(schedule_path),
            "nokkel_md5": _md5(turnuskalender.nokkel_path(year_identifier)),
            "eksportert": datetime.datetime.now().replace(microsecond=0).isoformat(),
        },
        "rader": built["rader"],
        "hoppet_over": [
            {"rullenummer": r, "grunn": g} for r, g in built["hoppet_over"]
        ],
    }

    if out_path:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with gzip.open(out_path, "wt", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False)
        logger.info("roster export: %d rows -> %s", len(payload["rader"]), out_path)

    return payload
