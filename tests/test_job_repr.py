import datetime as dt

import pytest

from scheduler.job import Job, JobType
from scheduler.util import Weekday


from helpers import T_2021_5_26__3_55, T_2021_5_26__3_55_UTC, utc, foo, bar


@pytest.mark.parametrize(
    "job_type, timing, handle, params, max_attempts, weight, delay, start, stop, skip_missing, tzinfo, res",
    [
        (
            JobType.CYCLIC,
            dt.timedelta(hours=1),
            foo,
            None,
            1,
            1,
            True,
            T_2021_5_26__3_55,
            None,
            True,
            None,
            [
                "scheduler.Job(<JobType.CYCLIC: 1>, datetime.timedelta(seconds=3600), <function foo at 0x",
                ">, {}, 1, 1, True, datetime.datetime(2021, 5, 26, 3, 55), None, True, None)",
            ],
        ),
        (
            JobType.CYCLIC,
            dt.timedelta(hours=1),
            foo,
            None,
            0,
            1 / 3,
            False,
            T_2021_5_26__3_55_UTC,
            None,
            True,
            utc,
            [
                "scheduler.Job(<JobType.CYCLIC: 1>, datetime.timedelta(seconds=3600), <function foo at 0x",
                ">, {}, 0, 0.3333333333333333, False, datetime.datetime(2021, 5, 26, 3, 55, tzinfo=datetime.timezone.utc)",
                ", None, True, datetime.timezone.utc)",
            ],
        ),
        (
            JobType.MINUTELY,
            dt.time(second=20),
            bar,
            {"msg": "foobar"},
            20,
            0,
            True,
            T_2021_5_26__3_55,
            T_2021_5_26__3_55 + dt.timedelta(minutes=10),
            False,
            None,
            [
                "scheduler.Job(<JobType.MINUTELY: 2>, datetime.time(0, 0, 20), <function bar at 0x",
                ">, {'msg': 'foobar'}, 20, 0, True, datetime.datetime(2021, 5, 26, 3, 55), datetime.datetime(2021, 5, 26, 4, 5), False, None)",
            ],
        ),
        (
            JobType.HOURLY,
            dt.time(hour=7, minute=5, tzinfo=utc),
            print,
            None,
            0,
            20,
            False,
            T_2021_5_26__3_55_UTC,
            T_2021_5_26__3_55_UTC + dt.timedelta(hours=20),
            False,
            utc,
            [
                "scheduler.Job(<JobType.HOURLY: 3>, datetime.time(7, 5, tzinfo=datetime.timezone.utc), <built-in function print>",
                ", {}, 0, 20, False, datetime.datetime(2021, 5, 26, 3, 55, tzinfo=datetime.timezone.utc),",
                " datetime.datetime(2021, 5, 26, 23, 55, tzinfo=datetime.timezone.utc), False, datetime.timezone.utc)",
            ],
        ),
        (
            JobType.DAILY,
            dt.time(hour=7, minute=5),
            foo,
            None,
            7,
            1,
            True,
            T_2021_5_26__3_55,
            None,
            True,
            None,
            [
                "scheduler.Job(<JobType.DAILY: 4>, datetime.time(7, 5), <function foo at 0x",
                ">, {}, 7, 1, True, datetime.datetime(2021, 5, 26, 3, 55), None, True, None)",
            ],
        ),
        (
            JobType.WEEKLY,
            Weekday.MONDAY,
            bar,
            None,
            0,
            1,
            False,
            T_2021_5_26__3_55_UTC,
            None,
            True,
            utc,
            [
                "scheduler.Job(<JobType.WEEKLY: 5>, <Weekday.MONDAY: 0>, <function bar at 0x",
                ">, {}, 0, 1, False, datetime.datetime(2021, 5, 26, 3, 55, tzinfo=datetime.timezone.utc), None, True, datetime.timezone.utc)",
            ],
        ),
        (
            JobType.WEEKLY,
            [Weekday.WEDNESDAY, (Weekday.TUESDAY, dt.time(1, 2, 3, tzinfo=utc))],
            print,
            {"end": "FOO\n"},
            1,
            1,
            True,
            T_2021_5_26__3_55_UTC,
            T_2021_5_26__3_55_UTC + dt.timedelta(days=60),
            False,
            utc,
            [
                "scheduler.Job(<JobType.WEEKLY: 5>, [<Weekday.WEDNESDAY: 2>, (<Weekday.TUESDAY: 1>,",
                " datetime.time(1, 2, 3, tzinfo=datetime.timezone.utc))], <built-in function print>,",
                " {'end': 'FOO\\n'}, 1, 1, True, datetime.datetime(2021, 5, 26, 3, 55, tzinfo=datetime.timezone.utc),",
                " datetime.datetime(2021, 7, 25, 3, 55, tzinfo=datetime.timezone.utc), False, datetime.timezone.utc)",
            ],
        ),
    ],
)
def test_job_repr(
    job_type,
    timing,
    handle,
    params,
    max_attempts,
    weight,
    delay,
    start,
    stop,
    skip_missing,
    tzinfo,
    res,
):
    job = Job(
        job_type=job_type,
        timing=timing,
        handle=handle,
        params=params,
        max_attempts=max_attempts,
        weight=weight,
        delay=delay,
        start=start,
        stop=stop,
        skip_missing=skip_missing,
        tzinfo=tzinfo,
    )
    for r in res:
        assert r in repr(job)
