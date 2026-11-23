from datetime import datetime
from zoneinfo import ZoneInfo
from event_time import is_available, keep_available, event_deadline

ET=ZoneInfo("America/New_York")
def dt(day,h,m=0): return datetime(2026,11,day,h,m,tzinfo=ET)
e=[
    {"date":"2026-11-22","time":"2:00 PM - 4:00 PM"},
    {"date":"2026-11-22","time":"5:00 PM"},
    {"date":"2026-11-22","time":""},
    {"date":"2026-11-23","time":"10:00 AM - 11:00 AM"},
]
assert len(keep_available(e,True,dt(22,15)))==4
assert len(keep_available(e,True,dt(22,16)))==3
assert len(keep_available(e,True,dt(22,20)))==2
assert len(keep_available(e,True,dt(23,11)))==0
assert len(keep_available(e,False,dt(23,11)))==4
assert event_deadline({"date":"2026-11-22","time":"11:00 PM - 1:00 AM"}).day==23
assert not is_available({"date":"not-a-date","time":"2:00 PM"},dt(22,14))
# A multi-day 1891Connect event beginning Nov 21 remains visible until Nov 22 at 11:30 PM.
multi={"date":"2026-11-21","time":"7:00 PM - 11:30 PM (next day)"}
assert is_available(multi,dt(22,20))
assert is_available(multi,dt(22,23,29))
assert not is_available(multi,dt(22,23,30))
print("PASS: timezone-aware clock, same-day expiry, overnight ranges, missing time, invalid dates")
