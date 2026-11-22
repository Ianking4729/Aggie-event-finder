"""Audit events.csv without changing or inventing event details."""
import argparse
import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
import re
from urllib.parse import urlparse

from recommender import load_events

REVIEW_FIELDS = ("description", "date", "time", "location", "source_url")


def normalized_title(event):
    return re.sub(r"\s+", " ", event.get("title", "")).strip().casefold()


def review_flags(event):
    flags = [
        f"missing {field}"
        for field in REVIEW_FIELDS
        if not (event.get(field) or "").strip()
    ]
    try:
        date.fromisoformat(event.get("date", ""))
    except ValueError:
        flags.append("invalid date")
    url = urlparse(event.get("source_url", ""))
    if url.scheme not in {"http", "https"} or not url.netloc:
        flags.append("invalid source URL")
    return flags


def audit(events, today):
    tags = Counter(tag for event in events for tag in event["tags"])
    titles_by_date = Counter(
        (normalized_title(event), event.get("date", "")) for event in events
    )
    dates_by_title = defaultdict(set)
    for event in events:
        dates_by_title[normalized_title(event)].add(event.get("date", ""))
    repeated_titles = {
        title: sorted(dates)
        for title, dates in dates_by_title.items()
        if title and len(dates) > 1
    }
    ids = [event["event_id"] for event in events]
    flags_by_record = [review_flags(event) for event in events]
    flag_counts = Counter(flag for flags in flags_by_record for flag in flags)
    upcoming = 0
    past = 0
    invalid_dates = 0
    for event in events:
        try:
            event_date = date.fromisoformat(event.get("date", ""))
        except ValueError:
            invalid_dates += 1
        else:
            if event_date >= today:
                upcoming += 1
            else:
                past += 1
    return {
        "tags": tags,
        "duplicate_ids": len(ids) - len(set(ids)),
        "duplicate_title_dates": sum(count - 1 for count in titles_by_date.values()),
        "repeated_titles": repeated_titles,
        "flags_by_record": flags_by_record,
        "flag_counts": flag_counts,
        "upcoming": upcoming,
        "past": past,
        "invalid_dates": invalid_dates,
    }


def export_review_queue(events, flags_by_record, path):
    fields = [
        "event_id",
        "title",
        "date",
        "time",
        "location",
        "description",
        "tags",
        "source_url",
        "review_flags",
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for event, flags in zip(events, flags_by_record):
            if flags:
                row = {field: event.get(field, "") for field in fields[:-1]}
                row["tags"] = ";".join(event["tags"])
                row["review_flags"] = "; ".join(flags)
                writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--export",
        type=Path,
        help="Write records needing human verification to this CSV path.",
    )
    args = parser.parse_args()

    events = load_events()
    today = date.today()
    results = audit(events, today)
    print(f"Audit date: {today.isoformat()}")
    print(f"Total records: {len(events)}")
    print(f"Upcoming records: {results['upcoming']}")
    print(f"Past records retained in the source dataset: {results['past']}")
    print(f"Invalid dates: {results['invalid_dates']}")
    print(f"Duplicate event IDs: {results['duplicate_ids']}")
    print(f"Duplicate normalized title/date pairs: {results['duplicate_title_dates']}")
    print("Data quality flags:")
    for field in REVIEW_FIELDS:
        print(f"  missing {field}: {results['flag_counts'][f'missing {field}']}")
    print(f"  invalid source URL: {results['flag_counts']['invalid source URL']}")
    print("Listings by team-assigned tag (tags overlap):")
    for tag, count in results["tags"].most_common():
        print(f"  {tag}: {count}")

    flagged = [
        (event, flags)
        for event, flags in zip(events, results["flags_by_record"])
        if flags
    ]
    print(f"Records needing source/data review: {len(flagged)}")
    for event, flags in flagged[:10]:
        flags = ", ".join(flags)
        print(f"  {event['event_id']} {event['title']}: {flags}")

    print(
        f"Repeated titles on different dates: {len(results['repeated_titles'])} "
        "(may be recurring events; verify before merging)"
    )
    for title, dates in list(results["repeated_titles"].items())[:10]:
        print(f"  {title}: {', '.join(dates)}")
    if args.export:
        export_review_queue(events, results["flags_by_record"], args.export)
        print(f"Review queue written to {args.export}")


if __name__ == "__main__":
    main()
