"""
Shared helpers for working with the boat logbook SQLite database
(data/logbook.data), used by gpx_from_logbook.py and logbook_stats.py.
"""

import datetime
import math
import sqlite3
import sys

EARTH_RADIUS_NM = 3440.065  # mean Earth radius in nautical miles


def haversine_nm(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * EARTH_RADIUS_NM * math.asin(math.sqrt(a))

# Core Data / NSDate reference date (2001-01-01T00:00:00Z) expressed as a
# Unix timestamp.
APPLE_EPOCH_OFFSET = 978307200

STATUS_NAMES = {
    0: "Sailing",
    1: "Docked",
    2: "Motoring",
    3: "Anchored",
    4: "Motor-Sailing",
}

# Statuses under which the boat is actually underway.
MOVING_STATUSES = {"Sailing", "Motoring", "Motor-Sailing"}

# Shared colors so the GPX track colors and the stats-widget breakdown
# visually match on a post that has both.
STATUS_COLORS = {
    "Sailing": "#1a9850",       # green
    "Motoring": "#2166ac",      # blue
    "Motor-Sailing": "#f46d43", # orange
    "Anchored": "#6a51a3",      # purple
    "Docked": "#666666",        # gray
}


def status_name(row):
    return STATUS_NAMES.get(row["status"], f"Unknown({row['status']})")


def parse_date(s, tz_offset_hours=None):
    if tz_offset_hours is None:
        # Naive datetime: .timestamp() below interprets this using the
        # system's local timezone, whatever that currently is.
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    tz = datetime.timezone(datetime.timedelta(hours=tz_offset_hours))
    return datetime.datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=tz)


def to_apple_epoch(dt):
    return dt.timestamp() - APPLE_EPOCH_OFFSET


def iso_time(ts):
    dt = datetime.datetime.fromtimestamp(
        ts + APPLE_EPOCH_OFFSET, tz=datetime.timezone.utc
    )
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_points(db_path, start, end):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    start_ts = to_apple_epoch(start)
    # end date is treated as inclusive through the end of that day
    end_ts = to_apple_epoch(end + datetime.timedelta(days=1))

    rows = conn.execute(
        """
        SELECT ZCL_LAT AS lat, ZCL_LON AS lon, ZZEITSTEMPEL AS ts, ZSTATUS AS status
        FROM ZLOGRECORD
        WHERE ZZEITSTEMPEL >= ? AND ZZEITSTEMPEL < ?
          AND ZCL_LAT IS NOT NULL AND ZCL_LON IS NOT NULL
          -- exclude "Null Island" (0,0): a handful of entries have this as
          -- a bogus GPS fix, which otherwise shows up as a huge spurious
          -- jump in distance/track calculations
          AND NOT (ZCL_LAT = 0 AND ZCL_LON = 0)
        ORDER BY ZZEITSTEMPEL ASC
        """,
        (start_ts, end_ts),
    ).fetchall()
    conn.close()
    return rows


def add_date_range_args(parser):
    """Add the --db/--start/--end/--tz-offset/--utc options shared by the
    logbook scripts."""
    parser.add_argument("--db", default="data/logbook.data", help="Path to logbook sqlite file")
    parser.add_argument("--start", required=True, help="Start date, YYYY-MM-DD (inclusive)")
    parser.add_argument("--end", required=True, help="End date, YYYY-MM-DD (inclusive)")
    parser.add_argument(
        "--tz-offset",
        type=float,
        default=None,
        help="Fixed UTC offset in hours to interpret --start/--end with, instead of this machine's current local timezone",
    )
    parser.add_argument(
        "--utc",
        action="store_true",
        help="Interpret --start/--end as UTC calendar days",
    )


def resolve_date_range(args):
    """
    Turn parsed --start/--end/--tz-offset/--utc args into (start, end)
    datetimes, printing which UTC offset was used for transparency.
    """
    tz_offset_hours = 0.0 if args.utc else args.tz_offset  # None => system local timezone
    start = parse_date(args.start, tz_offset_hours)
    end = parse_date(args.end, tz_offset_hours)

    resolved_offset = (
        start.astimezone().utcoffset()
        if tz_offset_hours is None
        else datetime.timedelta(hours=tz_offset_hours)
    )
    offset_hours = resolved_offset.total_seconds() / 3600
    print(f"Interpreting --start/--end as UTC{offset_hours:+g}", file=sys.stderr)

    return start, end
