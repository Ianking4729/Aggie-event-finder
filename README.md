# Aggie Event Finder

A COMP365 group project by Cool Kids Inc.

This app helps North Carolina A&T students find campus events based on their interests.

## Live app

[Open Aggie Event Finder](https://aggie-event-finder-dx4evquzbtdozlujbj8hfx.streamlit.app/)

## How it works

Choose your interests and click **Find my events**. The app shows up to five matching events. Each shared tag adds one point.

## Run the app

Open a terminal in the project folder and run:

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## Files

- `app.py`: The web app.
- `recommender.py`: Finds matching events.
- `events.csv`: Event information and source links.
- `requirements.txt`: Required library.

## Notes

Tags were added by our team. Event details can change, so check the official source links.

ChatGPT and Cursor helped with research and coding. Google Stitch helped with the design.
