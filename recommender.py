"""Aggie Event Finder: original tag baseline plus an experimental TF-IDF model.

Run: python recommender.py
Install dependency: pip install scikit-learn

Tags are team-assigned labels, not official event categories.
"""
import csv
import re
from pathlib import Path

DATA_FILE = Path(__file__).parent / "events.csv"
SPORTS_TAGS = {"sports", "basketball", "football", "volleyball"}


def load_events(path=DATA_FILE):
    events = []
    with open(path, newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
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


def normalize_interests(user_tags):
    return {str(tag).strip().lower() for tag in (user_tags or []) if str(tag).strip()}


def recommend_events(events, user_tags, limit=3):
    """UNCHANGED baseline behavior: rank only by the count of shared tags."""
    wanted = normalize_interests(user_tags)
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


def recommend_tfidf(events, user_tags, limit=5):
    """Rank events by cosine similarity to the student's selected interests.

    Uses title, description, and manually assigned tags. Repeating tags/title
    gives those short, structured fields more influence than description text.
    A similarity of zero is excluded. Scores are not probabilities.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    wanted = sorted(normalize_interests(user_tags))
    if not wanted or not events or limit <= 0:
        return []
    documents = []
    token_sets = []
    for event in events:
        tags = " ".join(event.get("tags", []))
        title = event.get("title", "")
        description = event.get("description", "")
        documents.append(f"{tags} {tags} {tags} {title} {title} {description}".strip())
        token_sets.append(set(re.findall(r"[a-z0-9]+", f"{tags} {title} {description}".lower())))
    query = " ".join(wanted)
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform(documents + [query])
    except ValueError:  # Empty vocabulary after stopword filtering
        return []
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    order = sorted(range(len(events)), key=lambda i: (-scores[i], i))
    results = []
    for i in order:
        if scores[i] <= 0:
            continue
        # A query must match at least one *whole interest* in the event text.
        # This prevents false positives like "not-a-real-tag" matching "Real Talk".
        if not any(set(re.findall(r"[a-z0-9]+", interest)).issubset(token_sets[i])
                   for interest in wanted):
            continue
        event = events[i]
        results.append({
            "event_id": event["event_id"],
            "title": event["title"],
            "date": event["date"],
            "time": event["time"],
            "location": event["location"],
            "description": event["description"],
            "source_url": event["source_url"],
            "tags": event["tags"],
            "similarity": round(float(scores[i]), 4),
        })
        if len(results) >= limit:
            break
    return results


def diversify_sports(ranked, limit=5, max_sports=2):
    """Optional reranker: cap sports when relevant non-sports candidates exist.

    Apply only to a mixed-interest request, not a sports-only request.
    Supply a broader ranked candidate list than the final display limit.
    Does NOT manufacture matches or force irrelevant non-sports events.
    """
    selected = []
    sports_count = 0
    for event in ranked:
        is_sports = bool(set(event.get("tags", [])).intersection(SPORTS_TAGS))
        if is_sports and sports_count >= max_sports:
            continue
        selected.append(event)
        sports_count += int(is_sports)
        if len(selected) == limit:
            break
    # If there weren't enough non-sports matches, preserve coverage instead of
    # returning artificially few relevant recommendations.
    if len(selected) < limit:
        selected_ids = {e["event_id"] for e in selected}
        for event in ranked:
            if event["event_id"] not in selected_ids:
                selected.append(event)
                selected_ids.add(event["event_id"])
                if len(selected) == limit:
                    break
    return selected


def recommend_tfidf_balanced(events, user_tags, limit=5, max_sports=2):
    wanted = normalize_interests(user_tags)
    ranked = recommend_tfidf(events, user_tags, limit=len(events))
    # A sports-specific search should still return the best sports events.
    if wanted and wanted.issubset(SPORTS_TAGS):
        return ranked[:limit]
    return diversify_sports(ranked, limit=limit, max_sports=max_sports)


def show_results(events, user_tags):
    label = ", ".join(user_tags) if user_tags else "(none)"
    results = recommend_events(events, user_tags)
    print(f"Tags we tried: {label}")
    if not results:
        print("No events matched those tags.\n")
        return
    for item in results:
        tags = ", ".join(item["shared_tags"])
        place = item["location"] if item["location"] else "location not listed"
        when = item["date"]
        if item["time"]:
            when += " " + item["time"]
        print(f"{item['event_id']} {item['title']} ({item['match_count']} matching tag(s): {tags})")
        print(f"  {when} at {place}\n")


if __name__ == "__main__":
    events = load_events()
    print(f"Loaded {len(events)} events.\n")
    for interests in (["academic", "career"], ["sports"], ["tech", "career", "sports"], ["not-a-real-tag"], []):
        print("=" * 65)
        show_results(events, interests)
        for name, function in (("TF-IDF", recommend_tfidf), ("TF-IDF + diversity", recommend_tfidf_balanced)):
            results = function(events, interests, limit=5)
            print(f"{name} ({', '.join(interests) or 'none'}):")
            if not results:
                print("  No matching results")
            for r in results:
                print(f"  {r['event_id']} {r['title']} | similarity={r['similarity']:.4f} | tags={','.join(r['tags'])}")
            print()
