# -*- coding: utf-8 -*-

from googleapiclient.http import BatchHttpRequest

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../api/google-calendar')))  # noqa
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # noqa
os.environ['DJANGO_SETTINGS_MODULE'] = 'pyclist.settings'  # noqa

from django import setup
setup()  # noqa

from common import service
from clist.models import Resource
from clist.models import Contest
from django.utils import timezone
from pytz import UTC

from datetime import datetime, timedelta

batch = BatchHttpRequest()


def create_resource_calendar(resource, calendarId=None):
    body = {
        "summary": resource.host,
        "location": resource.url,
        "selected": True,
    }
    if calendarId:
        entry = service.calendars().update(calendarId=calendarId, body=body).execute()
        if entry["id"] != resource.uid:
            raise Exception("Different id calendar for %s, excepted '%s', found '%s'" % (resource,
                                                                                         resource.uid,
                                                                                         entry["id"]))
    else:
        entry = service.calendars().insert(body=body).execute()
        resource.uid = entry["id"]
        resource.save()


def create_contest_event(calendarId, contest, eventId=None):
    body = {
        "summary": contest.title,
        "start": {"dateTime": contest.start_time.isoformat()},
        "end": {"dateTime": contest.end_time.isoformat()},
        "description": "Link: %s\nUpdated: %s\n" % (contest.url, contest.modified.strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
        "visibility": "public",
        "status": "confirmed",
        "transparency": "transparent",
        "attendees": [{"email": "clist.x10.mx@gmail.com", "responseStatus": "accepted"}],
    }
    if eventId:
        entry = service.events().update(calendarId=calendarId, eventId=eventId, body=body).execute()
        if entry["id"] != contest.uid:
            raise Exception("Different id event for %s, excepted '%s', found '%s'" % (contest,
                                                                                      contest.uid,
                                                                                      entry["id"]))
    else:
        entry = service.events().insert(calendarId=calendarId, body=body).execute()
        contest.uid = entry["id"]
        contest.save()
    return entry


def get_time_with_tz(time, tz=UTC):
    return timezone.make_aware(datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ"), tz)


def main():
    now = timezone.now()
    print(now)
    print()
    current = now - timedelta(days=8)

    calendars = dict(
        (entry["id"], entry)
        for entry in service.calendarList().list().execute()["items"]
    )

    print("Calendars:")
    for c in list(calendars.values()):
        if c["summary"] == "Дни рождения":
            continue
        print("    %(summary)s, %(id)s" % c)
    for r in Resource.objects.all():
        if r.uid:
            if r.uid not in calendars:
                raise Exception("Calendar with id='%s' not found, resource %s" % (r.uid, r.host))
            if calendars[r.uid]["summary"] != r.host:
                print("!   %s" % r)
                create_resource_calendar(r, r.uid)
        else:
            print("+   %s" % r)
            create_resource_calendar(r)

    for r in Resource.objects.all():
        events = dict(
            (entry["id"], entry)
            for entry in service.events().list(calendarId=r.uid, timeMin=current.isoformat()).execute()["items"]
        )
        contests = Contest.visible.filter(resource=r, end_time__gt=current)

        print("%s <%d event(s), %d contest(s)>:" % (r, len(events), len(contests)))
        for c in contests:
            if not c.uid or c.uid not in events:
                create_contest_event(r.uid, c)
                print("+   %s" % c)
            elif get_time_with_tz(events[c.uid]["updated"]) < c.modified - timedelta(minutes=1):
                entry = create_contest_event(r.uid, c, c.uid)
                updated = get_time_with_tz(entry["updated"])
                if c.modified - updated > timedelta(minutes=1):
                    print("!   %s" % c)

        for e in list(events.values()):
            if not Contest.visible.filter(resource=r, uid=e["id"]):
                print("-   %s" % e["summary"])
                service.events().delete(calendarId=r.uid, eventId=e["id"]).execute()


if __name__ == "__main__":
    main()
