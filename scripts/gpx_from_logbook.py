#!/usr/bin/env python3
"""
Generate a GPX track from the boat logbook SQLite database (data/logbook.data),
for a given date range. Points are grouped into one <trk> per sailing status
(Sailing / Motoring / Motor-Sailing / Anchored / Docked) so a GPX consumer
(e.g. a Leaflet map) can color each one differently.

Usage:
    python3 scripts/gpx_from_logbook.py --start 2026-03-01 --end 2026-03-15 \
        --out content/posts/season4/.../route.gpx

--start/--end are calendar days, inclusive. By default they're interpreted
in whatever timezone this machine is currently set to (so running it while
you're in a different timezone, as you travel with the boat, just works
without having to pass anything). Pass --tz-offset to use a fixed UTC
offset instead, or --utc for UTC day boundaries.
"""

import argparse
import sys
from xml.sax.saxutils import escape

from logbook_common import (
    MOVING_STATUSES,
    STATUS_COLORS,
    STATUS_NAMES,
    add_date_range_args,
    fetch_points,
    iso_time,
    resolve_date_range,
)

# Break a *stationary* leg (Anchored/Docked) into a new, unconnected run
# whenever the gap between consecutive points exceeds this many seconds --
# this is meant to catch a genuine unlogged passage or the boat being laid
# up, not an ordinary overnight or weekend at anchor/dock. Moving legs are
# never broken on time alone; see MOVING_STATUSES above.
DEFAULT_MAX_GAP_SECONDS = 24 * 60 * 60


def group_into_tracks(rows, max_gap_seconds):
    """
    Walk the time-ordered rows and build colored line runs where the status
    of a point describes the leg *leading out of* it (i.e. the boat was
    doing that status from this point until the next one). Consecutive
    points keep that leg's status as their color.

    A status change doesn't break the line: the point where the status
    changes is shared as the last point of the outgoing run and the first
    point of the incoming run, so e.g. a single sparse "Motoring" point
    between a "Sailing" point and an "Anchored" point still draws as a
    connected two-point line instead of an isolated marker.

    A moving leg (Sailing/Motoring/Motor-Sailing) is never broken on time
    alone -- the status itself guarantees the boat was underway the whole
    interval, however sparse the check-ins. A stationary leg (Anchored/
    Docked) *does* break when the gap exceeds max_gap_seconds, since a long
    gap there more likely hides an unlogged passage than a long nap at
    anchor.

    Returns a list of (status_name, [rows]) runs, each with >= 1 point.
    """
    if not rows:
        return []

    runs = []
    current_points = [rows[0]]
    current_status = STATUS_NAMES.get(rows[0]["status"], f"Unknown({rows[0]['status']})")

    for i in range(len(rows) - 1):
        p_a, p_b = rows[i], rows[i + 1]
        gap = p_b["ts"] - p_a["ts"]
        leg_status = STATUS_NAMES.get(p_a["status"], f"Unknown({p_a['status']})")

        if leg_status not in MOVING_STATUSES and gap > max_gap_seconds:
            runs.append((current_status, current_points))
            current_points = [p_b]
            current_status = STATUS_NAMES.get(p_b["status"], f"Unknown({p_b['status']})")
            continue

        if leg_status != current_status:
            # p_a is already the last point of current_points (appended as
            # the previous iteration's p_b), so it's naturally shared as
            # the first point of the new run too -- don't duplicate it.
            runs.append((current_status, current_points))
            current_points = [p_a]
            current_status = leg_status

        current_points.append(p_b)

    runs.append((current_status, current_points))
    return runs


def runs_to_tracks(runs):
    """
    Each run becomes its own <trk> (so a genuine time-gap break renders as
    a separate, unconnected polyline). Multiple runs can share the same
    status name/color.
    """
    return [(status_name, [points]) for status_name, points in runs]


def write_gpx(tracks, out_path):
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(
        '<gpx version="1.1" creator="gpx_from_logbook.py" '
        'xmlns="http://www.topografix.com/GPX/1/1" '
        'xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3">'
    )

    for status_name, segments in tracks:
        color = STATUS_COLORS.get(status_name, "#000000")
        lines.append("  <trk>")
        lines.append(f"    <name>{escape(status_name)}</name>")
        lines.append("    <extensions>")
        lines.append(f"      <gpxx:DisplayColor>{escape(color)}</gpxx:DisplayColor>")
        lines.append("    </extensions>")
        for points in segments:
            lines.append("    <trkseg>")
            for row in points:
                lines.append(
                    f'      <trkpt lat="{row["lat"]:.6f}" lon="{row["lon"]:.6f}">'
                )
                lines.append(f"        <time>{iso_time(row['ts'])}</time>")
                lines.append("      </trkpt>")
            lines.append("    </trkseg>")
        lines.append("  </trk>")

    lines.append("</gpx>")

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_date_range_args(parser)
    parser.add_argument("--out", required=True, help="Output .gpx path")
    parser.add_argument(
        "--max-gap-minutes",
        type=float,
        default=DEFAULT_MAX_GAP_SECONDS / 60,
        help="Break a stationary (Anchored/Docked) leg when the gap between points exceeds this many minutes; moving legs are never broken on time",
    )
    args = parser.parse_args()

    start, end = resolve_date_range(args)
    if end < start:
        print("error: --end must not be before --start", file=sys.stderr)
        sys.exit(1)

    rows = fetch_points(args.db, start, end)
    if not rows:
        print(f"No logbook points found between {args.start} and {args.end}", file=sys.stderr)
        sys.exit(1)

    runs = group_into_tracks(rows, args.max_gap_minutes * 60)
    tracks = runs_to_tracks(runs)
    write_gpx(tracks, args.out)

    print(f"Wrote {len(rows)} points across {len(runs)} run(s) to {args.out}")
    for status_name, segs in tracks:
        n_points = sum(len(s) for s in segs)
        print(f"  {status_name}: {n_points} points")


if __name__ == "__main__":
    main()
