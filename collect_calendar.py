"""Scrape NC A&T's public university calendar into an UNVERIFIED review queue.

Only publicly visible detail pages are considered. No logins, browser bypass,
or fabricated descriptions; every extracted row retains its original URL.
The candidate CSV is not merged automatically: a team member must verify each
source, time, venue and cancellation status first.

Usage: python collect_calendar.py --output calendar_candidates.csv
"""
import argparse
import csv
import re
import time
from datetime import date
from event_time import eastern_now
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

HOST = 'www.ncat.edu'
INDEX = f'https://{HOST}/calendar/index.php'
BOT = 'AggieEventFinderClassProject/1.0 (public calendar research; respectful requests)'
FIELDS = ['title','date','time','location','description','tags','source_url','review_status']
DATE_RE=re.compile(r'\b(0?[1-9]|1[0-2])/(0?[1-9]|[12]\d|3[01])/(20\d\d)\b')
EVENT_PATH=re.compile(r'^/calendar/20\d\d/\d\d/[^/?#]+\.php$')


def event_links(index_html):
    soup=BeautifulSoup(index_html,'html.parser')
    out={}
    for a in soup.find_all('a',href=True):
        url=urljoin(INDEX,a['href'])
        u=urlparse(url)
        if u.hostname==HOST and EVENT_PATH.match(u.path):
            out[url]=a.get_text(' ',strip=True)
    return out


def field_after_label(soup, label):
    """Extract a nearby published value without inventing missing fields."""
    wanted = label.casefold() + ':'
    for elem in soup.find_all(['p', 'span', 'div', 'strong']):
        if elem.get_text(' ', strip=True).casefold() != wanted:
            continue
        sibling = elem.find_next_sibling()
        if sibling:
            val = sibling.get_text(' ', strip=True)
            if val and not val.endswith(':'):
                return val
        nxt=elem.find_next(['p', 'div', 'span'])
        if nxt and nxt is not elem:
            val = nxt.get_text(' ', strip=True)
            if val and not val.endswith(':'):
                return val
    return ''


def parse_event(html,url, fallback=''):
    soup=BeautifulSoup(html,'html.parser')
    title=(soup.find('h1').get_text(' ',strip=True) if soup.find('h1') else fallback)
    text=soup.get_text(' ',strip=True)
    match=DATE_RE.search(text)
    event_date=''
    if match:
        try:
            event_date=date(int(match[3]),int(match[1]),int(match[2])).isoformat()
        except ValueError:pass
    # Information is a candidate until a human checks the source. Avoid making
    # guesses when page markup differs or the event has no known details.
    when=field_after_label(soup,'Time')
    where=field_after_label(soup,'Where')
    desc=''
    heading=soup.find(string=re.compile(r'^\s*Details:\s*$',re.I))
    if heading:
        for node in heading.parent.find_all_next(['p','h2','h3'],limit=6):
            content=node.get_text(' ',strip=True)
            if len(content)>25 and 'Download as iCal' not in content:
                desc=content[:500]
                break
    return dict(title=title,date=event_date,time=when,location=where,description=desc,
                tags='',source_url=url,review_status='needs_manual_source_verification')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='calendar_candidates.csv')
    parser.add_argument('--limit',type=int,default=80)
    args=parser.parse_args()
    if args.limit<1 or args.limit>100:
        raise SystemExit('limit must be 1 to 100')
    session=requests.Session(); session.headers['User-Agent']=BOT
    robots=RobotFileParser(); robots.set_url(f'https://{HOST}/robots.txt')
    try:
        robots.read()
    except Exception as exc:
        raise SystemExit(f'Cannot read robots.txt; not scraping: {exc}')
    if not robots.can_fetch(BOT,INDEX):
        raise SystemExit('robots.txt does not permit calendar index fetch')
    response=session.get(INDEX,timeout=20);response.raise_for_status()
    urls=event_links(response.text)
    results=[]
    for url, fallback in list(urls.items())[:args.limit]:
        if not robots.can_fetch(BOT,url): continue
        time.sleep(1)
        try:
            res=session.get(url,timeout=20);res.raise_for_status()
            event=parse_event(res.text,url,fallback)
            if event['date'] and event['date']>=eastern_now().date().isoformat():
                results.append(event)
        except requests.RequestException as exc:
            print(f'Skipped {url}: {exc}')
    with open(args.output,'w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(results)
    print(f'Exported {len(results)} unverified candidates to {args.output}')
    print('Review every candidate before moving verified data into events.csv.')

if __name__=='__main__':main()
