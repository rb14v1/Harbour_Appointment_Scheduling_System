from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from django.conf import settings

SLOT_MINUTES = 15


def app_timezone():
    return ZoneInfo(settings.TIME_ZONE)


def now_utc():
    return datetime.now(timezone.utc)


def local_date_string(moment):
    return moment.astimezone(app_timezone()).date().isoformat()


def is_on_grid(moment):
    return moment.second == 0 and moment.microsecond == 0 and moment.minute % SLOT_MINUTES == 0


def slot_starts(start, end):
    step = timedelta(minutes=SLOT_MINUTES)
    current = start
    while current < end:
        yield current
        current += step
