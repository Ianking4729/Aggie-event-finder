# Aggie Event Finder — Checkpoint 2 integration

This package combines the team's supplied `app.py` with the tested Checkpoint 2 recommender prototype.

## Live app

[Open Aggie Event Finder](https://aggie-event-finder-dx4evquzbtdozlujbj8hfx.streamlit.app/)

## Run the app (VS Code terminal)

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

The app opens in a browser. Select interests such as **basketball** and **social**, switch between **TF-IDF** and **Balanced TF-IDF**, and press **Find my events**. Keep **Upcoming events only** on for real upcoming recommendations. To reproduce the previously observed 5-sports vs 2-sports result on the full historical dataset, turn the upcoming filter **off** (the test experiment used the full dataset).

## Recheck backend tests

```bash
python3 checkpoint2_tests.py
```

## What's new

- Keeps the original navy-and-gold Streamlit design and tag-count baseline.
- Adds a selector for original baseline, TF-IDF, and balanced TF-IDF.
- Displays TF-IDF cosine similarity on each recommendation card, rather than assuming all recommendations have baseline `match_count` fields.
- Preserves the app's existing upcoming-event filtering.

## Limitations / responsible reporting

- Event categories are team-assigned tags, not official categories.
- Balanced TF-IDF only caps sports for mixed-interest queries when enough alternatives exist. It is **not yet validated as more accurate**.
- The dataset includes past events and has incomplete fields; the app's Upcoming toggle filters old dates.
- External source URLs have not been checked in this integration; do not claim they are all valid.
- The integrated UI requires a local Streamlit run and visual verification on your machine before presenting it as working.
- Do not overwrite the team's shared repo without coordination. Make a branch or obtain team approval.
