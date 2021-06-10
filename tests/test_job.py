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


samples = [T_2021_5_26__3_55, T_2021_5_26__3_55]


def to_tzinfo_sample(sample: dt.datetime, tzinfo: dt.timezone) -> dt.datetime:
    return dt.datetime.combine(sample.date(), sample.time(), tzinfo)


class Foo:
    def foo():
        pass


def foo(bar=1):
    pass


def job_param_template(
    handle,
    exec_at,
    max_attempts,
    weight,
    offset,
    tzinfo,
    repr,
    string,
    patch_datetime_now,
):
    if tzinfo is None:
        return [
            handle,
            exec_at,
            max_attempts,
            weight,
            offset,
            tzinfo,
            repr,
            string,
            patch_datetime_now,
        ]
    return [
        handle,
        exec_at,
        max_attempts,
        weight,
        to_tzinfo_sample(offset, tzinfo),
        tzinfo,
        repr,
        string,
        [to_tzinfo_sample(sample, tzinfo) for sample in patch_datetime_now],
    ]


# TODO: adjust repr string
# @pytest.mark.xfail(strict=True)
@pytest.mark.parametrize(
    "handle, exec_at, max_attempts, weight, offset, tzinfo, repr, string, patch_datetime_now",
    [
        job_param_template(
            foo,
            dt.timedelta(seconds=5),
            0,
            1,
            T_2021_5_26__3_55,
            None,
            "<scheduler.Job: foo, 2021-05-26 03:55:05, 0:00:05, 0/inf, weight=1, tzinfo=None>",
            "foo(...) 2021-05-26 03:55:05 0:00:05 0/inf weight=1.000 tzinfo=None",
            samples,
        ),
        job_param_template(
            Foo.foo,
            dt.timedelta(minutes=5, seconds=59),
            5,
            0.5,
            T_2021_5_26__3_55,
            dt.timezone(dt.timedelta(hours=1)),
            "<scheduler.Job: Foo.foo, 2021-05-26 04:00:59+01:00, 0:05:59, 0/5, weight=0.5, tzinfo=UTC+01:00>",
            "Foo.foo(...) 2021-05-26 04:00:59+01:00 0:05:59 0/5 weight=0.500 tzinfo=UTC+01:00",
            samples,
        ),
        job_param_template(
            foo,
            dt.timedelta(seconds=2),
            5,
            0.5,
            T_2021_5_26__3_55,
            dt.timezone(dt.timedelta(hours=-2, seconds=1)),
            "<scheduler.Job: foo, 2021-05-26 03:55:02-01:59:59, 0:00:02, 0/5, weight=0.5, tzinfo=UTC-01:59:59>",
            "foo(...) 2021-05-26 03:55:02-01:59:59 0:00:02 0/5 weight=0.500 tzinfo=UTC-01:59:59",
            samples,
        ),
    ],
    indirect=["patch_datetime_now"],
)
def test_repr(
    handle,
    exec_at,
    max_attempts,
    weight,
    offset,
    tzinfo,
    repr,
    string,
    patch_datetime_now,
):
    job = Job(
        handle,
        exec_at,
        max_attempts=max_attempts,
        weight=weight,
        offset=offset,
        tzinfo=tzinfo,
    )
    assert job.__repr__() == repr
    assert job.__str__() == string
