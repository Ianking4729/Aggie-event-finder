# Campus event page. Matching stays in recommender.py.

import html
from datetime import date, datetime

import streamlit as st

from recommender import load_events, recommend_events

PAGE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Space+Grotesk:wght@700&display=swap');

html, body, [class*="css"] {
  font-family: "Plus Jakarta Sans", sans-serif;
}

.stApp {
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(3, 60, 184, 0.35), rgba(4, 19, 41, 0) 70%),
    radial-gradient(circle at 90% 8%, rgba(253, 185, 39, 0.14), transparent 36%),
    #041329;
  color: #d6e3ff;
}

.block-container {
  max-width: 760px;
  padding-top: 4.75rem;
  padding-bottom: 2.5rem;
}

footer {visibility: hidden;}

.brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.85rem;
}
.brand h1 {
  margin: 0;
  font-size: 1.35rem;
  line-height: 1.2;
  color: #ffdca3;
}
.campus-pill {
  display: inline-block;
  margin-top: 0.2rem;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  border: 1px solid rgba(253, 185, 39, 0.35);
  background: rgba(253, 185, 39, 0.12);
  color: #fdb927;
  font-family: "Space Grotesk", sans-serif;
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.glass {
  position: relative;
  overflow: hidden;
  margin-bottom: 1rem;
  padding: 1.1rem 1.15rem 1rem;
  border-radius: 0.85rem;
  background: rgba(13, 28, 50, 0.82);
  border: 1px solid rgba(213, 196, 173, 0.14);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.28);
}
.glass::before,
.glass::after {
  content: "";
  position: absolute;
  border-radius: 999px;
  pointer-events: none;
  filter: blur(28px);
}
.glass::before {
  width: 140px;
  height: 140px;
  right: -30px;
  top: -40px;
  background: rgba(253, 185, 39, 0.16);
}
.glass::after {
  width: 120px;
  height: 120px;
  left: -36px;
  bottom: -46px;
  background: rgba(3, 60, 184, 0.28);
}
.kicker {
  color: #ffdd93;
  font-family: "Space Grotesk", sans-serif;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.glass h2 {
  margin: 0.2rem 0 0.45rem;
  font-size: 1.7rem;
  line-height: 1.15;
  color: #d6e3ff;
}
.glass h2 span { color: #fdb927; }
.glass p, .section-copy {
  margin: 0;
  color: #d5c4ad;
  line-height: 1.45;
}
.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.85rem;
}
.meta-chip {
  padding: 0.35rem 0.7rem;
  border-radius: 0.6rem;
  background: rgba(17, 32, 54, 0.85);
  color: #d6e3ff;
  font-size: 0.85rem;
}

.st-key-interest_panel {
  margin-bottom: 1rem;
  padding: 0.85rem 0.9rem 0.35rem;
  border-radius: 0.85rem;
  background: rgba(13, 28, 50, 0.88);
  border: 1px solid rgba(213, 196, 173, 0.14);
}
.st-key-find_events button {
  background: #fdb927;
  color: #422d00;
  border: none;
  font-weight: 700;
}
.st-key-find_events button:hover {
  border: none;
  color: #422d00;
}
div[data-testid="stPills"] button[aria-pressed="true"] {
  background: rgba(253, 185, 39, 0.18);
  color: #fdb927;
  border-color: rgba(253, 185, 39, 0.45);
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: end;
  margin: 0.2rem 0 0.35rem;
}
.section-head h2 {
  margin: 0;
  font-size: 1.45rem;
}
.count-pill {
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
  background: #1c2a41;
  color: #d5c4ad;
  font-family: "Space Grotesk", sans-serif;
  font-size: 0.68rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  white-space: nowrap;
}

.event-card {
  margin: 0 0 1rem;
  border-radius: 0.85rem;
  overflow: hidden;
  background: rgba(13, 28, 50, 0.92);
  border: 1px solid rgba(213, 196, 173, 0.12);
  transition: transform 0.2s ease, border-color 0.2s ease;
}
.event-card:hover {
  transform: translateY(-2px);
  border-color: rgba(253, 185, 39, 0.45);
}
.card-banner {
  position: relative;
  height: 92px;
}
.date-ribbon {
  position: absolute;
  top: 12px;
  left: 12px;
  min-width: 52px;
  padding: 0.3rem 0.4rem 0.35rem;
  border-radius: 0.55rem;
  background: #fdb927;
  color: #6c4c00;
  text-align: center;
  line-height: 1;
}
.date-ribbon span {
  display: block;
  font-family: "Space Grotesk", sans-serif;
  font-size: 0.68rem;
  letter-spacing: 0.06em;
}
.date-ribbon strong {
  font-size: 1.25rem;
}
.card-body { padding: 0.9rem 1rem 1rem; }
.when, .where, .blurb {
  margin: 0.15rem 0;
  color: #d5c4ad;
  font-size: 0.92rem;
}
.card-body h3 {
  margin: 0.25rem 0 0.35rem;
  color: #d6e3ff;
  font-size: 1.15rem;
  line-height: 1.3;
}
.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.7rem;
}
.tag {
  padding: 0.12rem 0.5rem;
  border-radius: 999px;
  background: #27354c;
  color: #b7c4ff;
  font-family: "Space Grotesk", sans-serif;
  font-size: 0.68rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.match-line {
  margin: 0.7rem 0 0;
  color: #fdb927;
  font-weight: 700;
}
.card-link {
  display: inline-block;
  margin-top: 0.75rem;
  color: #fdb927;
  font-weight: 700;
  text-decoration: none;
}
.card-link:hover { text-decoration: underline; }

.empty-state {
  padding: 1rem 1.05rem;
  border-radius: 0.85rem;
  background: rgba(28, 42, 65, 0.75);
  border: 1px solid rgba(183, 196, 255, 0.18);
  color: #d6e3ff;
}
.empty-state p { margin: 0.35rem 0 0; color: #d5c4ad; }

.view-bar {
  display: flex;
  gap: 1.25rem;
  margin: 0 0 0.8rem;
  padding: 0.55rem 0.2rem 0.15rem;
}
.view-bar span {
  color: #9d8f79;
  font-family: "Space Grotesk", sans-serif;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.view-bar .on { color: #fdb927; }

.rise { animation: rise 0.45s ease both; }
@keyframes rise {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .rise, .event-card {
    animation: none !important;
    transition: none !important;
  }
  .event-card:hover { transform: none; }
}
</style>
"""


def parse_keywords(text):
    # Commas separate extra interests. Each word is also tried as a tag.
    found = []
    for chunk in (text or "").replace(";", ",").split(","):
        piece = chunk.strip().lower()
        if not piece:
            continue
        for tag in [piece, *piece.split()]:
            if tag not in found:
                found.append(tag)
    return found


def keep_events(events, upcoming_only, today=None):
    # Keep file order so equal scores still prefer the earlier event.
    if not upcoming_only:
        return list(events)
    today = today or date.today()
    kept = []
    for event in events:
        try:
            event_date = date.fromisoformat(event["date"])
        except ValueError:
            continue
        if event_date >= today:
            kept.append(event)
    return kept


def pretty_when(iso_date, clock):
    try:
        parsed = datetime.strptime(iso_date, "%Y-%m-%d")
        day_text = f"{parsed.strftime('%a, %b')} {parsed.day}"
    except ValueError:
        day_text = iso_date or "Not listed"
    return f"{day_text} · {clock.strip() or 'Not listed'}"


def ribbon_parts(iso_date):
    try:
        parsed = datetime.strptime(iso_date, "%Y-%m-%d")
    except ValueError:
        return "---", "--"
    return parsed.strftime("%b").upper(), f"{parsed.day:02d}"


def safe_url(url):
    if url.startswith("https://") or url.startswith("http://"):
        return url
    return ""


def render_card(event, shared_tags=None, match_count=None):
    month, day = ribbon_parts(event.get("date", ""))
    title = html.escape(event.get("title") or "Untitled event")
    where = html.escape((event.get("location") or "").strip() or "Not listed")
    when = html.escape(pretty_when(event.get("date", ""), event.get("time") or ""))
    description = (event.get("description") or "").strip()
    blurb = f"<p class='blurb'>{html.escape(description)}</p>" if description else ""

    tags = shared_tags if shared_tags is not None else event.get("tags", [])
    tag_html = "".join(f"<span class='tag'>{html.escape(tag)}</span>" for tag in tags)
    score = ""
    if match_count is not None:
        word = "tag" if match_count == 1 else "tags"
        score = f"<p class='match-line'>{match_count} matching {word}</p>"

    link = ""
    url = safe_url(event.get("source_url") or "")
    if url:
        link = (
            f"<a class='card-link' href='{html.escape(url, quote=True)}' "
            "target='_blank' rel='noopener'>View official event</a>"
        )

    number = int(event.get("event_id") or "0")
    # No photo was verified, so the banner is only a navy and gold gradient.
    shift = (number % 4) * 18
    banner = (
        "linear-gradient(135deg, #0d1c32 0%, "
        f"#033cb8 {42 + shift}%, #6c4c00 130%)"
    )
    # Keep this as one HTML block. A blank line would make Markdown show the tags as text.
    card = (
        f"<article class='event-card'>"
        f"<div class='card-banner' style='background: {banner};'>"
        f"<div class='date-ribbon'><span>{month}</span><strong>{day}</strong></div>"
        f"</div>"
        f"<div class='card-body'>"
        f"<p class='when'>{when}</p>"
        f"<h3>{title}</h3>"
        f"<p class='where'>{where}</p>"
        f"{blurb}"
        f"<div class='tag-row'>{tag_html}</div>"
        f"{score}{link}"
        f"</div></article>"
    )
    st.html(card)


def clear_filters():
    st.session_state.interest_search = ""
    st.session_state.interest_pills = []
    st.session_state.extra_keywords = ""
    st.session_state.upcoming_only = True
    st.session_state.query_tags = []
    st.session_state.searched = False


def run_search():
    selected = list(st.session_state.get("interest_pills") or [])
    extra = parse_keywords(st.session_state.get("extra_keywords") or "")
    tags = []
    for tag in selected + extra:
        if tag and tag not in tags:
            tags.append(tag)
    st.session_state.query_tags = tags
    st.session_state.searched = True


def visible_tags(all_tags):
    query = (st.session_state.get("interest_search") or "").strip().lower()
    visible = [tag for tag in all_tags if query in tag]
    for tag in st.session_state.get("interest_pills") or []:
        if tag not in visible:
            visible.append(tag)
    return visible


def main():
    st.set_page_config(page_title="Aggie Event Finder", page_icon="✨", layout="centered")
    if "searched" not in st.session_state:
        st.session_state.searched = False
        st.session_state.query_tags = []
        st.session_state.played_intro = False
    st.session_state.setdefault("upcoming_only", True)
    st.session_state.setdefault("motion_on", True)

    events = load_events()
    all_tags = sorted({tag for event in events for tag in event["tags"]})
    first_day = datetime.strptime(events[0]["date"], "%Y-%m-%d")
    last_day = datetime.strptime(events[-1]["date"], "%Y-%m-%d")
    date_span = (
        f"{first_day.strftime('%b')} {first_day.day}, {first_day.year}"
        f" – {last_day.strftime('%b')} {last_day.day}, {last_day.year}"
    )
    motion = st.session_state.get("motion_on", True)
    intro = "rise" if motion and not st.session_state.played_intro else ""

    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    st.html(
        """
        <div class="brand">
          <div>
            <h1>Aggie Event Finder</h1>
            <span class="campus-pill">NC A&T Campus</span>
          </div>
        </div>
        """
    )
    st.html(
        f"""
        <section class="glass {intro}">
          <div class="kicker">NC A&T Campus Pulse</div>
          <h2>Find your next <span>Aggie experience</span></h2>
          <p>Choose interests to rank events from the dataset. Dates below come from the event file.</p>
          <div class="meta-row">
            <span class="meta-chip">{html.escape(date_span)}</span>
            <span class="meta-chip">Greensboro, NC</span>
          </div>
        </section>
        """
    )

    with st.container(key="interest_panel"):
        st.markdown("##### Your Campus Interests")
        st.text_input(
            "Search interests",
            key="interest_search",
            placeholder="Search interests, e.g. tech, arts",
            label_visibility="collapsed",
        )
        choices = visible_tags(all_tags)
        if choices:
            st.pills(
                "Tap interests to match",
                choices,
                selection_mode="multi",
                format_func=str.capitalize,
                key="interest_pills",
                wrap=True,
            )
        else:
            st.caption("No interests match that search.")
        st.text_input(
            "Additional interests or keywords",
            key="extra_keywords",
            placeholder="e.g. sports, career",
        )
        st.toggle("Upcoming events only", key="upcoming_only")
        st.toggle("Motion", key="motion_on")
        st.button("Find my events", key="find_events", type="primary", width="stretch", on_click=run_search)
        st.button("Reset filters", key="reset_filters", width="stretch", on_click=clear_filters)

    today = date.today()
    pool = keep_events(events, st.session_state.get("upcoming_only", True), today)
    searched = st.session_state.searched
    if searched:
        heading = "Recommended for you"
        results = recommend_events(pool, st.session_state.query_tags, limit=5)
        count_text = f"{len(results)} matches"
    else:
        heading = "Upcoming events"
        results = pool
        count_text = f"{len(results)} campus events"

    discovery_class = "" if searched else "on"
    recommended_class = "on" if searched else ""
    if st.session_state.get("upcoming_only", True):
        filter_note = (
            f"Events on or after {today.strftime('%b')} {today.day}, {today.year} stay in the list."
        )
    else:
        filter_note = "Upcoming is off, so earlier dates stay in the list too."
    st.html(
        f"""
        <div class="view-bar" aria-label="Current view">
          <span class="{discovery_class}">Discovery</span>
          <span class="{recommended_class}">Recommended</span>
        </div>
        <div class="section-head">
          <h2>{heading}</h2>
          <span class="count-pill">{count_text}</span>
        </div>
        <p class="section-copy">{filter_note}</p>
        """
    )

    if searched and not st.session_state.query_tags:
        st.html(
            """
            <div class="empty-state">
              <strong>Add an interest first.</strong>
              <p>Select a tag or type a keyword, then press Find my events.</p>
            </div>
            """
        )
    elif searched and not results:
        st.html(
            """
            <div class="empty-state">
              <strong>No events matched those interests.</strong>
              <p>Try another tag, or turn off Upcoming events only. Events with zero matches are not listed here.</p>
            </div>
            """
        )
    elif searched:
        used = ", ".join(st.session_state.query_tags)
        st.caption(f"Matched on {used}. Higher scores are listed first.")
        for event in results:
            render_card(event, event["shared_tags"], event["match_count"])
    else:
        st.caption("These are in date order. Press Find my events to rank them.")
        for event in results:
            render_card(event)

    # Entrance fade runs once, so later filter changes do not replay it.
    st.session_state.played_intro = True


if __name__ == "__main__":
    main()
