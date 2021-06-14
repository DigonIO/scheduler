import datetime as dt

import pytest

from scheduler import SchedulerError
from scheduler.job import Job, JobExecTimer
from scheduler.util import Weekday

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
def test_JobExecTimer_calc_next_exec_dt(start_dt, exec_at, target, next_target):
    timer = JobExecTimer(exec_at, start_dt)
    timer.calc_next_exec_dt()
    assert timer.datetime == target
    timer.calc_next_exec_dt()
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
    timer.calc_next_exec_dt()
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
    "handle, exec_at, max_attempts, weight, offset, tzinfo, _repr, string, patch_datetime_now",
    [
        job_param_template(
            foo,
            dt.timedelta(seconds=5),
            0,
            1,
            T_2021_5_26__3_55,
            None,
            [
                "scheduler.Job(<function foo at 0x",
                ", datetime.timedelta(seconds=5), {}, 0, 1, True, datetime.datetime(2021, 5, 26, 3, 55), False, None)",
            ],
            "foo(...) 2021-05-26 03:55:05 tz=None 0:00:05 0/inf w=1.000",
            samples,
        ),
        job_param_template(
            Foo.foo,
            dt.timedelta(minutes=5, seconds=59),
            5,
            0.5,
            T_2021_5_26__3_55,
            dt.timezone(dt.timedelta(hours=1)),
            [
                "scheduler.Job(<function Foo.foo at 0x",
                ">, datetime.timedelta(seconds=359), {}, 5, 0.5, True, datetime.datetime(2021, 5, 26, 3, 55, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), False, datetime.timezone(datetime.timedelta(seconds=3600)))",
            ],
            "Foo.foo(...) 2021-05-26 04:00:59+01:00 tz=UTC+01:00 0:05:59 0/5 w=0.500",
            samples,
        ),
        job_param_template(
            foo,
            dt.timedelta(seconds=2),
            5,
            0.5,
            T_2021_5_26__3_55,
            dt.timezone(dt.timedelta(hours=-2, seconds=1)),
            [
                "scheduler.Job(<function foo at 0x",
                ">, datetime.timedelta(seconds=2), {}, 5, 0.5, True, datetime.datetime(2021, 5, 26, 3, 55, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=79201))), False, datetime.timezone(datetime.timedelta(days=-1, seconds=79201)))",
            ],
            "foo(...) 2021-05-26 03:55:02-01:59:59 tz=UTC-01:59:59 0:00:02 0/5 w=0.500",
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
    _repr,
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
    for substing in _repr:
        assert substing in repr(job)
    assert str(job) == string


TZ_ERROR_MSG = "can't use offset-naive and offset-aware datetimes together"
# @pytest.mark.skip()
@pytest.mark.parametrize(
    "exec_at, tzinfo, offset, err_msg",
    [
        (dt.time(), None, None, None),
        (dt.time(tzinfo=dt.timezone.utc), dt.timezone.utc, None, None),
        (
            dt.time(tzinfo=dt.timezone(dt.timedelta(hours=1))),
            dt.timezone.utc,
            None,
            None,
        ),
        (
            (Weekday.MONDAY, dt.time(tzinfo=dt.timezone.utc)),
            dt.timezone(dt.timedelta(hours=1)),
            None,
            None,
        ),
        (
            [dt.time(), dt.time(tzinfo=dt.timezone.utc)],
            dt.timezone.utc,
            None,
            TZ_ERROR_MSG,
        ),
        ([dt.time(), dt.time(tzinfo=dt.timezone.utc)], None, None, TZ_ERROR_MSG),
        (dt.time(tzinfo=dt.timezone.utc), None, None, TZ_ERROR_MSG),
        (dt.time(), dt.timezone.utc, None, TZ_ERROR_MSG),
        (dt.time(), dt.timezone.utc, dt.datetime.now(), TZ_ERROR_MSG),
        (dt.time(), dt.timezone.utc, dt.datetime.now(dt.timezone.utc), TZ_ERROR_MSG),
        (
            dt.time(tzinfo=dt.timezone.utc),
            dt.timezone.utc,
            dt.datetime.now(dt.timezone.utc),
            None,
        ),
    ],
)
def test_tzinfo(exec_at, tzinfo, offset, err_msg):
    if err_msg:
        with pytest.raises(SchedulerError, match=err_msg) as execinfo:
            job = Job(lambda: None, exec_at, offset=offset, tzinfo=tzinfo)
    else:
        job = Job(lambda: None, exec_at, offset=offset, tzinfo=tzinfo)
        assert job.tzinfo == tzinfo


def test_lt():
    job0 = Job(lambda: None, dt.timedelta())
    job1 = Job(lambda: None, dt.timedelta(seconds=1))
    assert job0 < job1


@pytest.mark.parametrize(
    "delta_m, offset_m, res_delta_m",
    (
        [20, 21, 41],
        [1, 21, 22],
        [1, 1, 1],
        [20, 20, 20],
        [20, 1, 20],
    ),
)
def test_skip(delta_m, offset_m, res_delta_m):
    delta = dt.timedelta(minutes=delta_m)
    offset = dt.timedelta(minutes=offset_m)
    res_delta = dt.timedelta(minutes=res_delta_m)
    jet = JobExecTimer(delta, T_2021_5_26__3_55, True)
    assert jet.datetime == T_2021_5_26__3_55
    jet.calc_next_exec_dt(T_2021_5_26__3_55 + offset)
    assert jet.datetime == T_2021_5_26__3_55 + res_delta
