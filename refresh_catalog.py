"""Produce a reproducible current/archived split and a possible-duplicate review.

Does not delete or rewrite any source record. Repeated sessions on different
calendar dates are distinct events and intentionally remain separate.
Usage: python refresh_catalog.py [--out-dir data_review]
"""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from event_time import eastern_now, is_available

FIELDS = ['event_id', 'title', 'date', 'time', 'location', 'description', 'tags', 'source_url']


def key_text(value):
    return re.sub(r"\s+", " ", (value or "").strip().casefold())


def duplicate_review(rows):
    groups = defaultdict(list)
    for row in rows:
        # Same title, date and start/end time on a shared source is likely a duplicate;
        # intentional recurring sessions on different dates are not.
        key = (key_text(row['title']), row['date'], key_text(row['time']))
        groups[key].append(row)
    reviews = []
    for _, group in groups.items():
        if len(group) > 1:
            for item in group:
                reviews.append({**item, 'duplicate_candidates': ';'.join(r['event_id'] for r in group)})
    return reviews


def export_file(path, fields, rows):
    with open(path, 'w', newline='', encoding='utf-8') as dest:
        w=csv.DictWriter(dest, fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',default='data_review')
    args=parser.parse_args()
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    with open(Path(__file__).with_name('events.csv'),newline='',encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    now=eastern_now()
    upcoming=[r for r in rows if is_available(r,now)]
    expired=[r for r in rows if not is_available(r,now)]
    duplicates=duplicate_review(rows)
    export_file(out/'upcoming_events.csv',FIELDS,upcoming)
    export_file(out/'archived_events.csv',FIELDS,expired)
    export_file(out/'duplicate_review.csv',FIELDS+['duplicate_candidates'],duplicates)
    summary={
       'generated_at_greensboro':now.isoformat(),
       'total':len(rows),'upcoming':len(upcoming),'archived':len(expired),
       'possible_duplicate_rows':len(duplicates),
       'upcoming_tag_counts':dict(Counter(t for r in upcoming for t in r['tags'].split(';') if t)),
       'missing_descriptions':sum(not r['description'].strip() for r in rows),
       'missing_times':sum(not r['time'].strip() for r in rows),
       'missing_locations':sum(not r['location'].strip() for r in rows),
    }
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    print(f'Wrote upcoming, archived, duplicate review, and summary files in {out}/')

if __name__=='__main__':main()
