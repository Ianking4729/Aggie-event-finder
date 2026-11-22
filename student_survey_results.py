"""Summarize consented, anonymous recommendation survey responses."""
import argparse
import csv
from pathlib import Path
from statistics import mean

METHODS = {
    "tag_baseline": "tag_baseline_relevance_1_5",
    "tfidf": "tfidf_relevance_1_5",
    "balanced_tfidf": "balanced_tfidf_relevance_1_5",
}


def load_consented_responses(path):
    responses = []
    excluded = 0
    with path.open(newline="", encoding="utf-8-sig") as file:
        for row_number, row in enumerate(csv.DictReader(file), start=2):
            if (row.get("consent_given") or "").strip().casefold() not in {
                "yes",
                "true",
                "1",
            }:
                excluded += 1
                continue

            ratings = {}
            for method, field in METHODS.items():
                try:
                    rating = int(row.get(field, ""))
                except ValueError as error:
                    raise ValueError(
                        f"Row {row_number}: {field} must be an integer from 1 to 5."
                    ) from error
                if rating < 1 or rating > 5:
                    raise ValueError(
                        f"Row {row_number}: {field} must be an integer from 1 to 5."
                    )
                ratings[method] = rating

            preferred = (row.get("preferred_method") or "").strip().casefold()
            if preferred not in METHODS:
                raise ValueError(
                    f"Row {row_number}: preferred_method must be one of "
                    f"{', '.join(METHODS)}."
                )
            responses.append({"ratings": ratings, "preferred": preferred})
    return responses, excluded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "responses",
        nargs="?",
        default="student_survey_responses.csv",
        help="Anonymous response CSV (defaults to student_survey_responses.csv).",
    )
    args = parser.parse_args()
    responses, excluded = load_consented_responses(Path(args.responses))

    print(f"Consented responses included: {len(responses)}")
    print(f"Non-consented responses excluded: {excluded}")
    if not responses:
        print("No ratings to summarize yet.")
        return

    for method in METHODS:
        ratings = [response["ratings"][method] for response in responses]
        print(f"{method} mean relevance (1-5): {mean(ratings):.2f}")

    preferences = {method: 0 for method in METHODS}
    for response in responses:
        preferences[response["preferred"]] += 1
    print("Preferred method counts:")
    for method, count in preferences.items():
        print(f"  {method}: {count}")


if __name__ == "__main__":
    main()
