# Read the event file and suggest events that share the student's tags.
# Tags are labels we added. They are not official categories.

import csv
from pathlib import Path

DATA_FILE = Path(__file__).parent / "events.csv"


def load_events(path=DATA_FILE):
    events = []

    with open(path, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            # The CSV stores tags as "academic;career", so split them into a list.
            tag_text = row.get("tags") or ""
            tags = [tag.strip().lower() for tag in tag_text.split(";") if tag.strip()]
            events.append({
                "event_id": row.get("event_id") or "",
                "title": row.get("title") or "",
                "date": row.get("date") or "",
                "time": row.get("time") or "",
                "location": row.get("location") or "",
                "tags": tags,
                "description": row.get("description") or "",
                "source_url": row.get("source_url") or "",
            })

    return events


def recommend_events(events, user_tags, limit=3):
    # Keep events that share tags, and put the ones with more matches first.
    # No tags means nothing can match, so the result is empty.
    if not user_tags:
        user_tags = []

    wanted = {tag.strip().lower() for tag in user_tags if tag and tag.strip()}
    ranked = []

    for event in events:
        shared = wanted.intersection(event["tags"])
        if not shared:
            continue

        ranked.append({
            "event_id": event["event_id"],
            "title": event["title"],
            "date": event["date"],
            "time": event["time"],
            "location": event["location"],
            "description": event["description"],
            "source_url": event["source_url"],
            "shared_tags": sorted(shared),
            "match_count": len(shared),
        })

    ranked.sort(key=lambda item: item["match_count"], reverse=True)
    return ranked[:limit]


def show_results(events, user_tags):
    label = ", ".join(user_tags) if user_tags else "(none)"
    results = recommend_events(events, user_tags)

    print(f"Tags we tried: {label}")
    if not results:
        print("No events matched those tags.")
        print()
        return

    for item in results:
        tags = ", ".join(item["shared_tags"])
        place = item["location"] if item["location"] else "location not listed"
        when = item["date"]
        if item["time"]:
            when += " " + item["time"]
        print(f"{item['event_id']} {item['title']} ({item['match_count']} matching tag(s): {tags})")
        print(f"  {when} at {place}")
        print()


if __name__ == "__main__":
    events = load_events()
    print(f"Loaded {len(events)} events.")
    print()

    show_results(events, ["academic", "career"])
    show_results(events, ["sports"])
    show_results(events, ["not-a-real-tag"])
    show_results(events, [])
