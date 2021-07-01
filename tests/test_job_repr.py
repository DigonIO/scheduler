import pytest

from scheduler.job import Job


from helpers import (
    job_args,
    job_args_utc,
)


@pytest.mark.parametrize(
    "job_kwargs, results",
    [
        (
            job_args,
            [
                [
                    "scheduler.Job(<JobType.CYCLIC: 1>, datetime.timedelta(seconds=3600), <function foo at 0x",
                    ">, {}, 1, 1, True, datetime.datetime(2021, 5, 26, 3, 55), None, True, None)",
                ],
                [
                    "scheduler.Job(<JobType.MINUTELY: 2>, datetime.time(0, 0, 20), <function bar at 0x",
                    ">, {'msg': 'foobar'}, 20, 0, False, datetime.datetime(2021, 5, 26, 3, 54, 15), datetime.datetime(2021, 5, 26, 4, 5), False, None)",
                ],
                [
                    "scheduler.Job(<JobType.DAILY: 4>, datetime.time(7, 5), <function foo at 0x",
                    ">, {}, 7, 1, True, datetime.datetime(2021, 5, 26, 3, 55), None, True, None)",
                ],
            ],
        ),
        (
            job_args_utc,
            [
                [
                    "scheduler.Job(<JobType.CYCLIC: 1>, datetime.timedelta(seconds=3600), <function foo at 0x",
                    ">, {}, 0, 0.3333333333333333, False, datetime.datetime(2021, 5, 26, 3, 54, 59, 999990, tzinfo=datetime.timezone.utc)",
                    ", None, True, datetime.timezone.utc)",
                ],
                [
                    "scheduler.Job(<JobType.HOURLY: 3>, datetime.time(7, 5, tzinfo=datetime.timezone.utc), <built-in function print>",
                    ", {}, 0, 20, False, datetime.datetime(2021, 5, 26, 3, 55, tzinfo=datetime.timezone.utc),",
                    " datetime.datetime(2021, 5, 26, 23, 55, tzinfo=datetime.timezone.utc), False, datetime.timezone.utc)",
                ],
                [
                    "scheduler.Job(<JobType.WEEKLY: 5>, <Weekday.MONDAY: 0>, <function bar at 0x",
                    ">, {}, 0, 1, False, datetime.datetime(2021, 5, 25, 3, 55, tzinfo=datetime.timezone.utc), None, True, datetime.timezone.utc)",
                ],
                [
                    "scheduler.Job(<JobType.WEEKLY: 5>, [<Weekday.WEDNESDAY: 2>, (<Weekday.TUESDAY: 1>,",
                    " datetime.time(23, 45, 59, tzinfo=datetime.timezone.utc))], <built-in function print>,",
                    " {'end': 'FOO\\n'}, 1, 1, True, datetime.datetime(2021, 6, 2, 3, 55, tzinfo=datetime.timezone.utc),",
                    " datetime.datetime(2021, 7, 25, 3, 55, tzinfo=datetime.timezone.utc), False, datetime.timezone.utc)",
                ],
            ],
        ),
    ],
)
def test_job_repr(job_kwargs, results):
    for kwargs, result in zip(job_kwargs, results):
        for res in result:
            assert res in repr(Job(**kwargs))
