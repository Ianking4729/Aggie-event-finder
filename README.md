# Aggie Event Finder

Aggie Event Finder helps NC A&T students discover campus events using selected interests. The project compares a tag-count baseline with TF-IDF text ranking and a relevance-first diversity reranker.

## Live app

[Open Aggie Event Finder](https://aggie-event-finder-dx4evquzbtdozlujbj8hfx.streamlit.app/)

The hosted app updates only when the repository changes are pushed and the Streamlit deployment rebuilds. Local changes are not automatically live.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Recommendation methods

- **Original baseline:** ranks by the number of selected tags shared with an event.
- **TF-IDF:** represents the selected interests and each event's tags, title, and description as weighted text vectors, then ranks by cosine similarity. The vectorizer uses English stop words and one- and two-word terms. Tags are repeated three times and titles twice in the text to emphasize these structured fields over free-form descriptions. TF-IDF gives more weight to informative terms than common terms; cosine similarity compares direction rather than document length. It is suitable for this small text-based catalog and does not require labeled student ratings. Similarity scores are rankings, not probabilities.
- **Balanced TF-IDF:** first uses the same relevance-qualified TF-IDF candidates, then limits sports-tagged results to two for mixed-interest searches when enough relevant non-sports candidates can fill the requested list. Sports-only searches are not capped. If there are not enough alternatives, the method keeps relevant sports results rather than adding unrelated events.

All TF-IDF recommendations must contain at least one complete selected interest in their tags, title, or description. Repeated titles are suppressed within a recommendation list so a recurring event does not occupy multiple top-five slots. Separate occurrences remain in the event catalog and discovery view.

## Reproducible evaluation

Run the existing behavior tests and the focused Checkpoint 3 tests:

```bash
python checkpoint2_tests.py
python checkpoint3_tests.py
```

Compare all three recommendation methods on fixed interest queries:

```bash
python checkpoint3_evaluation.py
```

Add `--upcoming-only` to evaluate only events dated today or later:

```bash
python checkpoint3_evaluation.py --upcoming-only
```

The offline comparison reports:

- **Tag agreement@5:** how many of the top-five events share a selected tag, based on the team's labels.
- **Tag coverage:** number of distinct tags represented in the top five.
- **Sports share:** sports-tagged results in the top five.
- **Repeated titles:** repeated normalized event titles in the list.

Tag agreement is a dataset-label proxy, not a measure of student-perceived relevance. The methods use these tags as input, so this offline metric cannot establish that recommendations are more useful to students. A student evaluation is still needed before making that claim.

On the full 98-record file for `basketball + social`, TF-IDF returns 5/5
sports-tagged events, while Balanced TF-IDF returns 2/5. Both have 5/5
tag-agreement on this query, and the balanced list covers four distinct tags
instead of two. This indicates that the reranker changes category exposure
without losing tag matches in this example; it does not establish that students
prefer the balanced list.

## Practice questions

1. **What does TF-IDF do here?** It weights terms by how often they occur in an event and how distinctive they are across the catalog. We compare the resulting interest and event vectors with cosine similarity. This is text ranking, not a trained classifier.
2. **Why use TF-IDF instead of a supervised model?** We do not yet have student relevance labels to train or validate a supervised model. TF-IDF is a transparent text-based approach we can compare with the existing tag-count baseline.
3. **Does a more diverse list mean better recommendations?** Not necessarily. For `basketball + social` in the full catalog, Balanced TF-IDF reduces sports results from 5/5 to 2/5 without changing tag-agreement@5 in this example. Student ratings are still needed to evaluate perceived relevance.

The upcoming-only corpus is more imbalanced: on the audit date 2026-11-22 it
contains 29 records, 25 tagged `sports` and 25 tagged `basketball`, with only
four `academic` and one `cultural` tag. Because tags overlap, these counts do
not sum to 29. With so few future non-sports listings, the reranker correctly
keeps relevant sports results rather than forcing unrelated events into the
list. Adding verified non-sports source events is necessary to improve future
category coverage.

## Dataset and maintenance

`events.csv` is the event catalog. Each record includes its date, time, location, description, team-assigned tags, and source URL. Tags are non-exclusive and are not official campus categories.

Current full-catalog tag counts are:

| Tag | Listings |
|---|---:|
| sports | 37 |
| academic | 31 |
| basketball | 31 |
| social | 19 |
| arts | 10 |
| career | 9 |
| tech | 8 |
| cultural | 8 |
| volleyball | 4 |
| spiritual | 3 |
| health | 3 |
| football | 2 |
| games | 2 |
| service | 1 |

These counts overlap because a listing can have multiple tags. The app hides past events by default, but the CSV is a manually maintained snapshot—not a live feed. To keep it current, review the official source links weekly, add newly announced events, correct details only after checking a source, and retain past records for audit/history. Run the audit before updating the hosted app:

```bash
python event_data_audit.py
python event_data_audit.py --export data_review_queue.csv
```

The audit reports tag counts, expired events, missing fields, malformed source URLs, duplicate IDs, exact title/date duplicates, and titles that recur on different dates. Repeated titles may be legitimate recurring events; verify them before changing the data. The optional CSV is a review queue, not an automatically corrected dataset. Do not invent missing descriptions or event details. The UI shows a clear placeholder for missing descriptions and links users back to the recorded source.

The current data audit found 98 records, 46 missing descriptions, 19 missing locations, 3 missing times, no missing dates, no malformed source URL formats, and no duplicate normalized title/date pairs. It also found five titles occurring on multiple dates; these may be valid series and require a source check. Source URLs are syntactically checked; the app does not automatically verify that a page is current or that its details still match the listing.

## Student evaluation and consent

No student survey results are stored in this repository yet. Before collecting responses, confirm any course or university requirements with the instructor. Recruit approximately 10 volunteers and compare the same interest queries across methods, preferably with the method order varied. Ask students to rate event relevance (1–5), choose which list they prefer, and optionally explain why. Report the sample size, rating averages, preference counts, and limitations; do not present offline tag metrics as survey results.

Use a required consent checkbox before the survey questions. State the expected
time, how answers will be used, and the team's contact/retention plan in the
actual form. Suggested text:

> I understand that this optional class-project activity asks me to review campus event recommendations and rate their relevance. Participation is voluntary and will not affect my grades or campus services; I may skip questions or stop before submitting. The team will not ask for my name, student ID, or email. My responses will be summarized for the course project.

Record responses only from people who select **I agree to participate**. Show
the same interest query with all three methods, vary the order of the lists,
ask participants to rate each list's relevance from 1–5, and ask which they
would prefer to use. Do not collect direct identifiers, and follow any
additional instructor or institutional guidance. Preserve the submitted
consent choice before recording a survey response.

Use [student_survey_template.csv](./student_survey_template.csv) to record
consented anonymous responses. Copy it to `student_survey_responses.csv`, use
only response numbers (not names or IDs), store method keys as
`tag_baseline`, `tfidf`, and `balanced_tfidf`, and record ratings from 1–5.
Response files are ignored by Git. After collecting responses, summarize them
with:

```bash
python student_survey_results.py student_survey_responses.csv
```

No student responses have been collected in this repository yet; do not report
survey results until the team has actually conducted the consented evaluation.

## Known limitations

- Many descriptions and some locations/times are missing. The audit makes these gaps visible, but only source verification can safely fill them.
- Source links can point to a general calendar or schedule and may change; verify event details at the source.
- TF-IDF uses lexical matching; it may miss synonyms or related concepts that are not present in the event text.
- Event collection is manual; upcoming filtering expires old events from the active view but does not discover new ones.
- Tag agreement and category coverage are proxies. Student ratings are required to assess perceived relevance.
