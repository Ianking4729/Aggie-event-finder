"""Reproduce an offline comparison of the three recommendation methods."""
import argparse
from collections import Counter
from datetime import date
import re

from recommender import (
    load_events,
    recommend_events,
    recommend_tfidf,
    recommend_tfidf_balanced,
)

LIMIT = 5
SPORTS_TAGS = {"sports", "basketball", "football", "volleyball"}
METHODS = (
    ("Tag-count baseline", recommend_events),
    ("TF-IDF", recommend_tfidf),
    ("Balanced TF-IDF", recommend_tfidf_balanced),
)
QUERIES = (
    ("career",),
    ("basketball", "social"),
    ("academic", "career"),
    ("arts", "cultural"),
)


def valid_events(events, today, upcoming_only):
    selected = []
    invalid_dates = 0
    for event in events:
        try:
            event_date = date.fromisoformat(event.get("date", ""))
        except ValueError:
            invalid_dates += 1
            continue
        if not upcoming_only or event_date >= today:
            selected.append(event)
    return selected, invalid_dates


def tags_for(event):
    return set(event.get("tags") or event.get("shared_tags") or [])


def title_key(event):
    return re.sub(r"\s+", " ", event.get("title", "")).strip().casefold()


def print_metrics(results, interests):
    if not results:
        print("no results")
        return
    wanted = {interest.casefold() for interest in interests}
    hits = sum(bool(tags_for(event).intersection(wanted)) for event in results)
    coverage = set().union(*(tags_for(event) for event in results)) if results else set()
    sports = sum(bool(tags_for(event).intersection(SPORTS_TAGS)) for event in results)
    titles = [title_key(event) for event in results if title_key(event)]
    duplicates = len(titles) - len(set(titles))
    print(
        f"tag-agreement@{LIMIT}={hits}/{len(results)}, "
        f"tag coverage={len(coverage)}, sports={sports}/{len(results)}, "
        f"repeated titles={duplicates}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--upcoming-only",
        action="store_true",
        help="Evaluate only events dated today or later.",
    )
    args = parser.parse_args()
    today = date.today()
    all_events = load_events()
    events, invalid_dates = valid_events(all_events, today, args.upcoming_only)
    categories = Counter(tag for event in events for tag in event["tags"])

    print(f"Offline evaluation date: {today.isoformat()}")
    corpus = "upcoming records" if args.upcoming_only else "all dated records"
    print(f"Evaluation corpus: {len(events)} {corpus} of {len(all_events)} total")
    print(f"Records skipped for invalid dates: {invalid_dates}")
    print("Listings in evaluation corpus by team-assigned tag (tags overlap):")
    for tag, count in categories.most_common():
        print(f"  {tag}: {count}")

    for interests in QUERIES:
        print(f"\nQuery: {', '.join(interests)}")
        for name, method in METHODS:
            results = method(events, interests, limit=LIMIT)
            print(f"{name}: ", end="")
            print_metrics(results, interests)

    print(
        "\nTag agreement is a dataset-label proxy, not a student relevance rating. "
        "Use student ratings for claims about perceived quality."
    )


if __name__ == "__main__":
    main()
