#!/usr/bin/env python3
"""Export the planned roster for one rutetermin as a flat file.

Produces one row per (rullenummer, date) — which dagsverk that driver is
rostered on, or which fri code they have — for the sibling nlfstreik app.

Usage:
    python scripts/export_turnusplan.py --year R26
    python scripts/export_turnusplan.py --year R26 --out /tmp/turnusplan_R26.json.gz

The output names 300+ drivers' entire working year, so treat it as PII: it
belongs in instance/protected/ on the receiving side, never under app/static/.
"""

import argparse
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Deliberately no os.environ.setdefault("DB_TYPE", ...) here — see the comment
# in scripts/import_innplassering.py for the incident that rule comes from.


def main():
    parser = argparse.ArgumentParser(
        description="Export the planned roster (rullenummer x date -> dagsverk)"
    )
    parser.add_argument("--year", required=True, help="Year identifier, e.g. R26")
    parser.add_argument("--out", help="Output path (.json.gz). Default: turnusdata/<year>/")
    parser.add_argument("--stasjonering", default="OSL",
                        help="Depot this roster covers (default OSL)")
    args = parser.parse_args()

    year_id = args.year.upper()

    from config import AppConfig
    from app.services.innplassering_service import get_innplassering_by_turnus_set
    from app.services.roster_export_service import export
    from app.services.turnus_service import get_turnus_set_by_year
    from app.utils import turnuskalender

    # Print which DB this is about to read — a wrong DB_TYPE here silently
    # exports an empty roster from an unrelated SQLite file.
    print(f"DB_TYPE={AppConfig.DB_TYPE}")

    turnus_set = get_turnus_set_by_year(year_id)
    if not turnus_set:
        print(f"Error: No turnus set found for year '{year_id}'")
        sys.exit(1)

    # TurnusSet stores an absolute path that goes stale when the data store
    # moves; fall back to the conventional location exactly as DataframeManager
    # does, rather than reporting "not found" for a file that is right there.
    schedule_path = turnus_set.get("turnus_file_path")
    if not schedule_path or not os.path.exists(schedule_path):
        fallback = turnuskalender.schedule_path(year_id)
        if schedule_path:
            print(f"  Note: stored path is stale ({schedule_path}); using {fallback}")
        schedule_path = fallback
    if not os.path.exists(schedule_path):
        print(f"Error: Turnus JSON not found: {schedule_path}")
        sys.exit(1)

    innplassering = get_innplassering_by_turnus_set(turnus_set["id"])
    if not innplassering:
        print(f"Error: No innplassering rows for turnus set {turnus_set['id']}. "
              f"Run scripts/import_innplassering.py --year {year_id} first.")
        sys.exit(1)

    out_path = args.out or os.path.join(
        AppConfig.turnusfiler_dir, year_id.lower(), f"turnusplan_{year_id}.json.gz"
    )

    print(f"Exporting {year_id} ({args.stasjonering})...")
    print(f"  Innplasserte: {len(innplassering)}")
    print(f"  Schedule:     {schedule_path}")

    try:
        payload = export(year_id, schedule_path, innplassering,
                         stasjonering=args.stasjonering, out_path=out_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(f"  Periode:      {payload['fra']} .. {payload['til']}")
    print(f"  Rader:        {len(payload['rader'])}")
    med_dagsverk = sum(1 for r in payload["rader"] if r["dv_nummer"])
    print(f"    på dagsverk: {med_dagsverk}")
    print(f"    fri/blank:   {len(payload['rader']) - med_dagsverk}")
    if payload["hoppet_over"]:
        print(f"  Hoppet over:  {len(payload['hoppet_over'])}")
        for row in payload["hoppet_over"][:10]:
            print(f"    {row['rullenummer']}: {row['grunn']}")
    print(f"OK: {out_path} ({os.path.getsize(out_path) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
