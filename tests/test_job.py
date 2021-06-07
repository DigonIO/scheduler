import pytest
import datetime as dt

from scheduler.util import (
    Weekday,
)
from scheduler.job import JobExecTimer, Job

T_2021_5_26__3_55 = dt.datetime(2021, 5, 26, 3, 55)  # a Wednesday


@pytest.mark.parametrize(
    "start_dt, exec_at, target, next_target",
    (
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            Weekday.THURSDAY,
            dt.datetime(year=2021, month=5, day=27),
            dt.datetime(year=2021, month=6, day=3),
        ],
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            dt.time(hour=12, minute=1),
            dt.datetime(year=2021, month=5, day=26, hour=12, minute=1),
            dt.datetime(year=2021, month=5, day=27, hour=12, minute=1),
        ],
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            (Weekday.FRIDAY, dt.time(hour=1, minute=1)),
            dt.datetime(year=2021, month=5, day=28, hour=1, minute=1),
            dt.datetime(year=2021, month=6, day=4, hour=1, minute=1),
        ],
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            dt.timedelta(hours=3, seconds=27),
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39)
            + dt.timedelta(hours=3, seconds=27),
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39)
            + dt.timedelta(hours=3, seconds=27)
            + dt.timedelta(hours=3, seconds=27),
        ],
    ),
)
def test_JobExecTimer_gen_next_exec_dt(start_dt, exec_at, target, next_target):
    timer = JobExecTimer(exec_at, start_dt)
    timer.gen_next_exec_dt()
    assert timer.datetime == target
    timer.gen_next_exec_dt()
    assert timer.datetime == next_target


@pytest.mark.parametrize(
    "start_dt, exec_at, target",
    (
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            Weekday.THURSDAY,
            dt.datetime(year=2021, month=5, day=27),
        ],
        [
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            dt.time(hour=12, minute=1),
            dt.datetime(year=2021, month=5, day=26, hour=12, minute=1),
        ],
    ),
)
def test_JobExecTimer_timedelta(start_dt, exec_at, target):
    timer = JobExecTimer(exec_at, start_dt)
    timer.gen_next_exec_dt()
    assert timer.timedelta(start_dt) == target - start_dt


@pytest.fixture
def patch_datetime_now(monkeypatch, request):
    class datetime_patch:
        it = iter(request.param)

        @classmethod
        def now(cls, tz=None):
            return next(cls.it)

    monkeypatch.setattr(dt, "datetime", datetime_patch)


samples = [
    T_2021_5_26__3_55,  # job creation
    T_2021_5_26__3_55 + dt.timedelta(seconds=5),  # t1
    T_2021_5_26__3_55 + dt.timedelta(seconds=8),  # t2
    T_2021_5_26__3_55 + dt.timedelta(seconds=11),  # t3
    T_2021_5_26__3_55 + dt.timedelta(hours=1, minutes=3),  # t4
    T_2021_5_26__3_55 + dt.timedelta(hours=2, minutes=2),  # t5
    T_2021_5_26__3_55 + dt.timedelta(days=1, minutes=2),  # t6
    T_2021_5_26__3_55 + dt.timedelta(days=9, minutes=7),  # t7
    T_2021_5_26__3_55 + dt.timedelta(days=10, minutes=7),  # t8
]


class Foo:
    def foo():
        pass


def foo(bar=1):
    pass


# TODO: adjust repr string
@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize(
    "handle, exec_at, max_attempts, weight, offset, tzinfo, repr, patch_datetime_now",
    [
        [
            foo,
            dt.timedelta(seconds=5),
            0,
            1,
            T_2021_5_26__3_55,
            None,
            "foo 1234s 0/inf w=1 tz=None",
            samples,
        ],
        [
            Foo.foo,
            dt.timedelta(seconds=5),
            5,
            0.5,
            T_2021_5_26__3_55,
            dt.timezone(dt.timedelta(hours=1)),
            "Foo.foo 1234s 0/5 w=0.5 tz=UTC+01:00",
            samples,
        ],
        [
            foo,
            dt.timedelta(seconds=2),
            5,
            0.5,
            T_2021_5_26__3_55,
            dt.timezone(dt.timedelta(hours=-2, seconds=1)),
            "foo 1234s 0/5 w=0.5 tz=UTC-01:59",
            samples,
        ],
    ],
    indirect=["patch_datetime_now"],
)
def test_repr(
    handle, exec_at, max_attempts, weight, offset, tzinfo, repr, patch_datetime_now
):
    job = Job(
        handle,
        exec_at,
        max_attempts=max_attempts,
        weight=weight,
        offset=offset,
        tzinfo=tzinfo,
    )
    assert job.__repr__ == repr
    assert job.__str__ == repr
