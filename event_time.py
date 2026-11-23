"""Eastern-time event expiry rules for the Aggie Event Finder.

An event with a published end time remains visible until that end time.
A listing with only a start time expires once that start time has passed
because we cannot safely infer its duration. A listing without a time remains
visible through the end of the published day (time unconfirmed).
"""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
import re

EASTERN = ZoneInfo("America/New_York")
CLOCK = re.compile(r"(?<!\w)(?:1[0-2]|0?[1-9]):?[0-5][0-9]?\s*(?:AM|PM)(?!\w)", re.I)


def eastern_now():
    return datetime.now(EASTERN)


def parse_clock(text):
    """Accept '2:00 PM', '2 PM', '2:00PM', and 24-hour '14:00'."""
    text = (text or "").strip().upper().replace(".", "")
    text = re.sub(r"\s+", " ", text)
    for pattern in ("%I:%M %p", "%I:%M%p", "%I %p", "%I%p", "%H:%M"):
        try:
            return datetime.strptime(text, pattern).time()
        except ValueError:
            pass
    return None


def event_deadline(event):
    """Return deadline for an event as a timezone-aware datetime or None."""
    try:
        event_date = date.fromisoformat(str(event.get("date") or ""))
    except ValueError:
        return None
    raw = str(event.get("time") or "").strip()
    # The calendar export may include a multi-day event whose closing clock
    # is later than the starting clock. In that case the time field explicitly
    # marks the end as "(next day)" rather than relying on an overnight guess.
    explicit_next_day = bool(re.search(r"\(next day\)\s*$", raw, re.I))
    raw = re.sub(r"\s*\(next day\)\s*$", "", raw, flags=re.I)
    # Convert a written range to start/end; parts without AM/PM inherit the
    # suffix from the right side, e.g. '12-1 p.m.' is not used in our CSV.
    chunks = re.split(r"\s+[-–—]\s+", raw)
    start = parse_clock(chunks[0]) if chunks else None
    end = parse_clock(chunks[-1]) if len(chunks) > 1 else None
    if end:
        # Treat a range ending before its start as an overnight event.
        deadline = datetime.combine(event_date, end, EASTERN)
        if explicit_next_day or (start and end < start):
            deadline += timedelta(days=1)
        return deadline
    if start:
        return datetime.combine(event_date, start, EASTERN)
    # No reliable time: let students see the event throughout its date.
    return datetime.combine(event_date + timedelta(days=1), time.min, EASTERN)


def is_available(event, now=None):
    now = now or eastern_now()
    if now.tzinfo is None:
        raise ValueError("now must have timezone info")
    cutoff = event_deadline(event)
    return cutoff is not None and cutoff > now


def keep_available(events, upcoming_only=True, now=None):
    if not upcoming_only:
        return list(events)
    now = now or eastern_now()
    return [event for event in events if is_available(event, now)]
