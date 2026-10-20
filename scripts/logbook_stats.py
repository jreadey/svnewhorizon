#!/usr/bin/env python3
"""
Print passage statistics for a date range from the boat logbook SQLite
database (data/logbook.data): distance traveled, start-to-end distance,
passage time, average speed, and percent time spent in each sailing status.

Usage:
    python3 scripts/logbook_stats.py --start 2026-10-17 --end 2026-10-18

If the range starts and/or ends at anchor or dock, the passage is trimmed
to the actual underway period: from the first point where status becomes
Sailing/Motoring/Motor-Sailing, to the point where it last stops being one
of those. If there's a stop partway through (e.g. Sailing -> Anchored ->
Sailing again), time and percentage spent Anchored/Docked during the
passage are reported too.

Average speed is distance traveled divided by total elapsed passage time
(including any stop along the way), not just time spent moving.

--start/--end are calendar days, inclusive, interpreted the same way as
gpx_from_logbook.py (local machine timezone by default; see --tz-offset
and --utc).
"""

import argparse
import json
import sys

from logbook_common import (
    MOVING_STATUSES,
    STATUS_COLORS,
    add_date_range_args,
    fetch_points,
    haversine_nm,
    iso_time,
    resolve_date_range,
    status_name,
)

# Display order for the time-by-status breakdown: moving statuses first,
# then stationary ones.
STATUS_DISPLAY_ORDER = ["Sailing", "Motoring", "Motor-Sailing", "Anchored", "Docked"]


def trim_to_underway(rows):
    """
    Trim leading/trailing Anchored/Docked points so the passage covers only
    the period the boat was actually moving:
      - start = first row whose status is a moving status (the point where
        motion began).
      - end = the point where the last moving leg ends: if the last moving-
        status row is also the last row overall, use it as-is (no arrival
        has been logged yet -- e.g. a passage still in progress); otherwise
        use the row right after it, since that's the point where status
        changed away from moving, i.e. where the boat actually stopped.

    Returns (trimmed_rows, start_idx, end_idx) using indices into `rows`,
    or None if no moving status is found at all in the range.
    """
    moving_indices = [i for i, r in enumerate(rows) if status_name(r) in MOVING_STATUSES]
    if not moving_indices:
        return None

    start_idx = moving_indices[0]
    last_moving_idx = moving_indices[-1]
    end_idx = last_moving_idx if last_moving_idx == len(rows) - 1 else last_moving_idx + 1

    return rows[start_idx : end_idx + 1], start_idx, end_idx


def compute_stats(rows):
    """
    rows: time-ordered points already trimmed to the underway period.
    A point's status describes the leg leading out of it (same convention
    as gpx_from_logbook.py), so time/distance for each inter-point leg is
    attributed to the status of the leg's starting point.

    Only moving legs (Sailing/Motoring/Motor-Sailing) count toward distance
    traveled. A stationary leg's two points are supposed to be at the same
    spot, but the position comes from whatever device is logging (e.g. a
    phone/iPad), which can wander off with a crew member -- a flight home
    while the boat sits Docked would otherwise get counted as miles
    sailed. Stationary legs still count toward time-by-status.
    """
    distance_nm = 0.0
    time_by_status = {}

    for i in range(len(rows) - 1):
        p_a, p_b = rows[i], rows[i + 1]
        leg_status = status_name(p_a)
        leg_seconds = p_b["ts"] - p_a["ts"]
        time_by_status[leg_status] = time_by_status.get(leg_status, 0.0) + leg_seconds
        if leg_status in MOVING_STATUSES:
            distance_nm += haversine_nm(p_a["lat"], p_a["lon"], p_b["lat"], p_b["lon"])

    start, end = rows[0], rows[-1]
    passage_seconds = end["ts"] - start["ts"]
    straight_line_nm = haversine_nm(start["lat"], start["lon"], end["lat"], end["lon"])
    avg_speed_kts = distance_nm / (passage_seconds / 3600) if passage_seconds > 0 else 0.0

    moving_seconds = sum(
        seconds for status, seconds in time_by_status.items() if status in MOVING_STATUSES
    )
    avg_speed_underway_kts = (
        distance_nm / (moving_seconds / 3600) if moving_seconds > 0 else 0.0
    )

    return {
        "start": start,
        "end": end,
        "passage_seconds": passage_seconds,
        "distance_nm": distance_nm,
        "straight_line_nm": straight_line_nm,
        "avg_speed_kts": avg_speed_kts,
        "avg_speed_underway_kts": avg_speed_underway_kts,
        "time_by_status": time_by_status,
    }


def format_duration(seconds, use_days=False):
    if use_days:
        total_hours = round(seconds / 3600)
        days, hours = divmod(total_hours, 24)
        return f"{days}d {hours:02d}h"
    total_minutes = round(seconds / 60)
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h {minutes:02d}m"


def date_only(ts):
    return iso_time(ts)[:10]


def print_report(stats, use_days=False):
    passage_hours = stats["passage_seconds"] / 3600

    print(f"Date range:         {date_only(stats['start']['ts'])} to {date_only(stats['end']['ts'])}")
    print(f"Passage start:      {iso_time(stats['start']['ts'])}  ({stats['start']['lat']:.5f}, {stats['start']['lon']:.5f})")
    print(f"Passage end:        {iso_time(stats['end']['ts'])}  ({stats['end']['lat']:.5f}, {stats['end']['lon']:.5f})")
    print(f"Passage time:       {format_duration(stats['passage_seconds'], use_days)} ({passage_hours:.2f} h)")
    print(f"Distance traveled:  {stats['distance_nm']:.1f} nm")
    print(f"Start-to-end dist:  {stats['straight_line_nm']:.1f} nm")
    print(f"Average speed:      {stats['avg_speed_kts']:.1f} kts  (distance / total elapsed passage time)")
    print(f"Avg speed underway: {stats['avg_speed_underway_kts']:.1f} kts  (distance / time actually Sailing, Motoring, or Motor-Sailing)")
    print()

    total_seconds = sum(stats["time_by_status"].values())
    print("Time by status:")
    seen = set()
    for name in STATUS_DISPLAY_ORDER:
        seconds = stats["time_by_status"].get(name, 0.0)
        seen.add(name)
        if seconds <= 0:
            continue
        pct = 100 * seconds / total_seconds if total_seconds > 0 else 0.0
        print(f"  {name:<14} {format_duration(seconds, use_days):>8}   {pct:5.1f}%")

    # Any unexpected status name not in the known display order.
    for name, seconds in stats["time_by_status"].items():
        if name in seen or seconds <= 0:
            continue
        pct = 100 * seconds / total_seconds if total_seconds > 0 else 0.0
        print(f"  {name:<14} {format_duration(seconds, use_days):>8}   {pct:5.1f}%")


def build_json_report(stats):
    """
    Turn the computed stats into a JSON-serializable dict for the
    passage-stats Hugo shortcode (layouts/shortcodes/passage-stats.html).
    """
    total_seconds = sum(stats["time_by_status"].values())
    breakdown = []
    for name in STATUS_DISPLAY_ORDER:
        seconds = stats["time_by_status"].get(name, 0.0)
        if seconds <= 0:
            continue
        breakdown.append(
            {
                "status": name,
                "hours": round(seconds / 3600, 2),
                "percent": round(100 * seconds / total_seconds, 1) if total_seconds > 0 else 0.0,
                "color": STATUS_COLORS.get(name, "#000000"),
            }
        )
    # Any unexpected status name not in the known display order.
    seen = set(STATUS_DISPLAY_ORDER)
    for name, seconds in stats["time_by_status"].items():
        if name in seen or seconds <= 0:
            continue
        breakdown.append(
            {
                "status": name,
                "hours": round(seconds / 3600, 2),
                "percent": round(100 * seconds / total_seconds, 1) if total_seconds > 0 else 0.0,
                "color": STATUS_COLORS.get(name, "#000000"),
            }
        )

    return {
        "start": {
            "time": iso_time(stats["start"]["ts"]),
            "lat": round(stats["start"]["lat"], 5),
            "lon": round(stats["start"]["lon"], 5),
        },
        "end": {
            "time": iso_time(stats["end"]["ts"]),
            "lat": round(stats["end"]["lat"], 5),
            "lon": round(stats["end"]["lon"], 5),
        },
        "passage_hours": round(stats["passage_seconds"] / 3600, 2),
        "distance_nm": round(stats["distance_nm"], 1),
        "straight_line_nm": round(stats["straight_line_nm"], 1),
        "avg_speed_kts": round(stats["avg_speed_kts"], 1),
        "avg_speed_underway_kts": round(stats["avg_speed_underway_kts"], 1),
        "status_breakdown": breakdown,
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    add_date_range_args(parser)
    parser.add_argument(
        "--json",
        metavar="PATH",
        help="Also write the stats as JSON to this path (for the passage-stats Hugo shortcode)",
    )
    parser.add_argument(
        "--days",
        action="store_true",
        help="Show durations as days/hours (e.g. '3d 06h') instead of hours/minutes (e.g. '78h 23m')",
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

    trimmed = trim_to_underway(rows)
    if trimmed is None:
        print(
            "No underway (Sailing/Motoring/Motor-Sailing) segment found in this range.",
            file=sys.stderr,
        )
        sys.exit(1)

    underway_rows, start_idx, end_idx = trimmed
    if len(underway_rows) < 2:
        print(
            "Only a single underway point found in this range -- not enough to compute a passage.",
            file=sys.stderr,
        )
        sys.exit(1)

    if start_idx > 0:
        print(f"(trimmed {start_idx} leading stationary point(s))", file=sys.stderr)
    if end_idx < len(rows) - 1:
        print(f"(trimmed {len(rows) - 1 - end_idx} trailing stationary point(s))", file=sys.stderr)

    stats = compute_stats(underway_rows)
    print_report(stats, use_days=args.days)

    if args.json:
        with open(args.json, "w") as f:
            json.dump(build_json_report(stats), f, indent=2)
        print(f"\nWrote JSON stats to {args.json}")


if __name__ == "__main__":
    main()
