import datetime as dt

import pytest

from scheduler import Scheduler, Weekday


def foo(msg="bar"):
    print(msg)


# NOTE: This test does not check if the jobs are executed at the correct time.
#       The behavioural tests for this purpose are in tests_core.py and tests_jobs.py
def test_general_readme():
    sch = Scheduler()

    sch.schedule(foo, dt.timedelta(minutes=10))  # every 10 minutes
    sch.schedule(foo, dt.time(hour=16, minute=45))  # every day at 16:45
    sch.schedule(foo, Weekday.MONDAY)  # every monday at 00:00

    # every monday at 16:45
    sch.schedule(
        foo,
        (Weekday.MONDAY, dt.time(hour=16, minute=45)),
    )

    # every friday at 00:00, every 10 minutes and every monday at 16:45
    sch.schedule(
        foo,
        [
            Weekday.FRIDAY,
            dt.timedelta(minutes=10),
            (Weekday.MONDAY, dt.time(hour=16, minute=45)),
        ],
    )

    sch.once(foo, dt.datetime(year=2021, month=2, day=11))  # at given datetime
    sch.once(foo, dt.timedelta(minutes=10))  # in 10 minutes

    sch.once(foo, dt.timedelta(seconds=10000), params={"msg": "fizz"})
    sch.schedule(foo, dt.timedelta(minutes=1), params={"msg": "buzz"})

    sch.exec_jobs()
