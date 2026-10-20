#!/usr/bin/env python3
"""
Create a cleaned-up copy of the boat logbook SQLite database
(data/logbook.data), fixing known data-quality issues found while building
the other logbook scripts. The original file is left untouched; a new file
is written and a report of every change is printed.

Usage:
    python3 scripts/clean_logbook.py --db data/logbook.data --out data/logbook_clean.data

What it does, to the ZLOGRECORD table only (every other table is copied
through unchanged):

  1. Removes rows that are exact timestamp duplicates (same ZZEITSTEMPEL),
     keeping the lowest Z_PK of each group.
  2. Removes rows at (0, 0) -- "Null Island" -- which the logging app itself
     uses as a sentinel for an invalid GPS fix.
  3. Where a moving status (Sailing/Motoring/Motor-Sailing) is left set for
     a long stretch (>= --stale-hours, default 24h) with essentially no
     movement (< --stale-speed-kts, default 0.3kts), changes that row's
     status to Docked -- most such cases look like the engine/sails were
     logged on and the status was never updated back after arrival.
  4. Flags (reports only, does not modify) any remaining leg with implied
     speed > --flag-speed-kts (default 20kts) for manual review, since it's
     often ambiguous whether that's a GPS error or a genuinely fast leg.
"""

import argparse
import shutil
import sqlite3
import sys

from logbook_common import MOVING_STATUSES, STATUS_NAMES, haversine_nm, iso_time

DEFAULT_STALE_HOURS = 24.0
DEFAULT_STALE_SPEED_KTS = 0.3
DEFAULT_FLAG_SPEED_KTS = 20.0

DOCKED_STATUS_CODE = next(code for code, name in STATUS_NAMES.items() if name == "Docked")


def fetch_all_rows(conn):
    return conn.execute(
        """
        SELECT Z_PK AS pk, ZCL_LAT AS lat, ZCL_LON AS lon, ZZEITSTEMPEL AS ts, ZSTATUS AS status
        FROM ZLOGRECORD
        WHERE ZCL_LAT IS NOT NULL AND ZCL_LON IS NOT NULL
        ORDER BY ZZEITSTEMPEL ASC, Z_PK ASC
        """
    ).fetchall()


def remove_duplicate_timestamps(conn, rows):
    removed = []
    i = 0
    while i < len(rows) - 1:
        j = i
        while j + 1 < len(rows) and rows[j + 1]["ts"] == rows[i]["ts"]:
            j += 1
        if j > i:
            # keep rows[i] (lowest Z_PK, since rows are ordered ts ASC, pk ASC)
            for k in range(i + 1, j + 1):
                removed.append(rows[k])
        i = j + 1

    if removed:
        conn.executemany(
            "DELETE FROM ZLOGRECORD WHERE Z_PK = ?", [(r["pk"],) for r in removed]
        )
    return removed


def remove_null_island(conn, rows):
    bad = [r for r in rows if r["lat"] == 0 and r["lon"] == 0]
    if bad:
        conn.executemany(
            "DELETE FROM ZLOGRECORD WHERE Z_PK = ?", [(r["pk"],) for r in bad]
        )
    return bad


def fix_stale_moving_status(conn, rows, stale_hours, stale_speed_kts):
    """
    rows must already have duplicates and Null Island points removed, and be
    time-ordered. A row's status describes the leg leading out of it (same
    convention as the other logbook scripts): if that leg lasts at least
    stale_hours with average speed under stale_speed_kts while tagged as a
    moving status, the row's status is changed to Docked.
    """
    changes = []
    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        status = STATUS_NAMES.get(a["status"], f"Unknown({a['status']})")
        if status not in MOVING_STATUSES:
            continue

        dt_hours = (b["ts"] - a["ts"]) / 3600
        if dt_hours < stale_hours:
            continue

        dist_nm = haversine_nm(a["lat"], a["lon"], b["lat"], b["lon"])
        speed_kts = dist_nm / dt_hours if dt_hours > 0 else 0.0
        if speed_kts >= stale_speed_kts:
            continue

        changes.append(
            {
                "pk": a["pk"],
                "ts": a["ts"],
                "lat": a["lat"],
                "lon": a["lon"],
                "old_status": status,
                "duration_hours": dt_hours,
                "distance_nm": dist_nm,
            }
        )

    if changes:
        conn.executemany(
            "UPDATE ZLOGRECORD SET ZSTATUS = ? WHERE Z_PK = ?",
            [(DOCKED_STATUS_CODE, c["pk"]) for c in changes],
        )
    return changes


def flag_fast_legs(rows, flag_speed_kts):
    """Report-only: legs (on the already-cleaned row set) with implied
    speed above flag_speed_kts. Nothing is modified."""
    flagged = []
    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        dt_hours = (b["ts"] - a["ts"]) / 3600
        if dt_hours <= 0:
            continue
        dist_nm = haversine_nm(a["lat"], a["lon"], b["lat"], b["lon"])
        speed_kts = dist_nm / dt_hours
        if speed_kts > flag_speed_kts:
            status = STATUS_NAMES.get(a["status"], f"Unknown({a['status']})")
            flagged.append(
                {
                    "ts": a["ts"],
                    "status": status,
                    "speed_kts": speed_kts,
                    "distance_nm": dist_nm,
                    "duration_hours": dt_hours,
                }
            )
    return flagged


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--db", default="data/logbook.data", help="Path to the source logbook sqlite file")
    parser.add_argument("--out", required=True, help="Path to write the cleaned sqlite file to")
    parser.add_argument(
        "--stale-hours",
        type=float,
        default=DEFAULT_STALE_HOURS,
        help=f"Minimum duration (hours) of near-zero movement under a moving status before it's corrected to Docked (default: {DEFAULT_STALE_HOURS})",
    )
    parser.add_argument(
        "--stale-speed-kts",
        type=float,
        default=DEFAULT_STALE_SPEED_KTS,
        help=f"Below this average speed (kts), a long moving-status leg is considered stationary (default: {DEFAULT_STALE_SPEED_KTS})",
    )
    parser.add_argument(
        "--flag-speed-kts",
        type=float,
        default=DEFAULT_FLAG_SPEED_KTS,
        help=f"Report (but don't modify) any leg with implied speed above this (default: {DEFAULT_FLAG_SPEED_KTS})",
    )
    args = parser.parse_args()

    shutil.copyfile(args.db, args.out)
    print(f"Copied {args.db} -> {args.out}")

    conn = sqlite3.connect(args.out)
    conn.row_factory = sqlite3.Row

    rows = fetch_all_rows(conn)
    print(f"Starting rows (non-null position): {len(rows)}")
    print()

    dup_removed = remove_duplicate_timestamps(conn, rows)
    print(f"Removed {len(dup_removed)} exact-duplicate-timestamp row(s):")
    for r in dup_removed:
        print(f"  pk={r['pk']}  {iso_time(r['ts'])}  ({r['lat']:.5f}, {r['lon']:.5f})")
    print()

    rows = [r for r in rows if r not in dup_removed]

    null_island_removed = remove_null_island(conn, rows)
    print(f"Removed {len(null_island_removed)} (0,0) Null Island row(s):")
    for r in null_island_removed:
        status = STATUS_NAMES.get(r["status"], f"Unknown({r['status']})")
        print(f"  pk={r['pk']}  {iso_time(r['ts'])}  status={status}")
    print()

    rows = [r for r in rows if r not in null_island_removed]

    stale_changes = fix_stale_moving_status(conn, rows, args.stale_hours, args.stale_speed_kts)
    print(
        f"Changed {len(stale_changes)} stale moving-status row(s) to Docked "
        f"(>= {args.stale_hours:g}h with < {args.stale_speed_kts:g}kts):"
    )
    for c in stale_changes:
        print(
            f"  pk={c['pk']}  {iso_time(c['ts'])}  "
            f"{c['old_status']} -> Docked  "
            f"({c['duration_hours']:.1f}h, {c['distance_nm']:.1f}nm)"
        )
    print()

    # Re-fetch the live row set (status values just changed) for the
    # report-only fast-leg scan.
    rows = fetch_all_rows(conn)
    flagged = flag_fast_legs(rows, args.flag_speed_kts)
    print(f"Flagged {len(flagged)} leg(s) with implied speed > {args.flag_speed_kts:g}kts (not modified):")
    for f in flagged:
        print(
            f"  {iso_time(f['ts'])}  status={f['status']}  "
            f"{f['speed_kts']:.1f}kts  ({f['distance_nm']:.1f}nm over {f['duration_hours']*60:.1f}min)"
        )
    print()

    conn.commit()
    conn.close()

    print(
        f"Done. {len(dup_removed)} duplicate(s) removed, "
        f"{len(null_island_removed)} Null Island row(s) removed, "
        f"{len(stale_changes)} status correction(s), "
        f"{len(flagged)} fast-leg warning(s) (unmodified)."
    )


if __name__ == "__main__":
    main()
