from recommender import (load_events, recommend_events, recommend_tfidf,
                         recommend_tfidf_balanced)

events = load_events()
assert len(events) == 98
assert len(recommend_events(events, ["academic", "career"])) == 3
assert recommend_events(events, ["not-a-real-tag"]) == []
assert recommend_tfidf(events, ["not-a-real-tag"]) == []
assert recommend_tfidf(events, []) == []
assert len(recommend_tfidf(events, ["sports"], limit=5)) == 5
assert len(recommend_tfidf_balanced(events, ["sports"], limit=5)) == 5
q = ["basketball", "social"]
raw = recommend_tfidf(events, q, limit=5)
balanced = recommend_tfidf_balanced(events, q, limit=5)
raw_sports = sum("sports" in e["tags"] for e in raw)
balanced_sports = sum("sports" in e["tags"] for e in balanced)
assert raw_sports == 5, raw_sports
assert balanced_sports == 2, balanced_sports
print("PASS: 8 checks, including baseline, empty/unmatched queries, and mixed-interest diversity")
print("basketball + social, original TF-IDF: ", raw_sports, "sports of 5")
print("basketball + social, balanced TF-IDF: ", balanced_sports, "sports of 5")
print("Balanced top 5:")
for i, event in enumerate(balanced, 1):
    print(f"{i}. {event['title']} | {','.join(event['tags'])} | cosine={event['similarity']:.4f}")
