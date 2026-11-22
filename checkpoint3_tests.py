import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from recommender import recommend_events, recommend_tfidf, recommend_tfidf_balanced
from student_survey_results import load_consented_responses


def event(event_id, title, tags, description=""):
    return {
        "event_id": event_id,
        "title": title,
        "date": "2027-01-15",
        "time": "2:00 PM",
        "location": "Campus",
        "tags": tags,
        "description": description,
        "source_url": "https://example.edu/event",
    }


events = [
    event("s1", "Basketball Showcase", ["sports", "basketball"]),
    event("s2", "Basketball Skills Clinic", ["sports", "basketball"]),
    event("s3", "Basketball Club Game", ["sports", "basketball"]),
    event("s4", "Basketball Club Game", ["sports", "basketball"]),
    event("n1", "Social Campus Mixer", ["social"]),
    event("n2", "Social Student Meetup", ["social"]),
    event("n3", "Social Student Hangout", ["social"]),
    event("x1", "Art Gallery Opening", ["arts"]),
]

raw = recommend_tfidf(events, ["basketball", "social"], limit=5)
balanced = recommend_tfidf_balanced(events, ["basketball", "social"], limit=5)
baseline = recommend_events(events, ["basketball", "social"], limit=5)
assert len({event["title"].casefold() for event in baseline}) == len(baseline)
assert len({event["title"].casefold() for event in raw}) == len(raw)
assert len({event["title"].casefold() for event in balanced}) == len(balanced)
assert sum("sports" in event["tags"] for event in balanced) <= 2
assert all(event["matched_interests"] for event in balanced)
assert all(event["event_id"] != "x1" for event in balanced)
assert recommend_tfidf_balanced(events, ["basketball"], limit=0) == []

sports_only = recommend_tfidf_balanced(events[:4], ["basketball"], limit=5)
assert len(sports_only) == 3
assert all("basketball" in event["tags"] for event in sports_only)

shortage = recommend_tfidf_balanced(events[:4], ["basketball", "social"], limit=5)
assert len(shortage) == 3
assert all("basketball" in event["tags"] for event in shortage)

with TemporaryDirectory() as directory:
    response_file = Path(directory) / "responses.csv"
    columns = [
        "response_number",
        "consent_given",
        "query_tags",
        "display_order",
        "tag_baseline_relevance_1_5",
        "tfidf_relevance_1_5",
        "balanced_tfidf_relevance_1_5",
        "preferred_method",
    ]
    with response_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerow({
            "response_number": "1",
            "consent_given": "yes",
            "query_tags": "career",
            "display_order": "tfidf,tag_baseline,balanced_tfidf",
            "tag_baseline_relevance_1_5": "3",
            "tfidf_relevance_1_5": "4",
            "balanced_tfidf_relevance_1_5": "5",
            "preferred_method": "balanced_tfidf",
        })
        writer.writerow({"response_number": "2", "consent_given": "no"})
    responses, excluded = load_consented_responses(response_file)
    assert len(responses) == 1
    assert excluded == 1

print(
    "PASS: relevance-first diversity, sports-only behavior, title suppression, "
    "and consent-filtered survey parsing"
)
