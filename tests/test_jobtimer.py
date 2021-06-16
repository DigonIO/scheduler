import datetime as dt

import pytest

from scheduler import SchedulerError
from scheduler.job import Job, JobTimer, JobType, sane_timing_types
from scheduler.util import Weekday

T_2021_5_26__3_55 = dt.datetime(2021, 5, 26, 3, 55)  # a Wednesday
utc = dt.timezone.utc


@pytest.mark.parametrize(
    "job_type, timing, start, target, next_target",
    (
        [
            JobType.WEEKLY,
            Weekday.THURSDAY,
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39, tzinfo=utc),
            dt.datetime(year=2021, month=5, day=27, tzinfo=utc),
            dt.datetime(year=2021, month=6, day=3, tzinfo=utc),
        ],
        [
            JobType.WEEKLY,
            (Weekday.FRIDAY, dt.time(hour=1, minute=1, tzinfo=utc)),
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39, tzinfo=utc),
            dt.datetime(year=2021, month=5, day=28, hour=1, minute=1, tzinfo=utc),
            dt.datetime(year=2021, month=6, day=4, hour=1, minute=1, tzinfo=utc),
        ],
        [
            JobType.DAILY,
            dt.time(hour=12, minute=1, tzinfo=utc),
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39, tzinfo=utc),
            dt.datetime(year=2021, month=5, day=26, hour=12, minute=1, tzinfo=utc),
            dt.datetime(year=2021, month=5, day=27, hour=12, minute=1, tzinfo=utc),
        ],
        [
            JobType.HOURLY,
            dt.time(minute=1, tzinfo=utc),
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39, tzinfo=utc),
            dt.datetime(year=2021, month=5, day=26, hour=12, minute=1, tzinfo=utc),
            dt.datetime(year=2021, month=5, day=26, hour=13, minute=1, tzinfo=utc),
        ],
        [
            JobType.MINUTELY,
            dt.time(second=1, tzinfo=utc),
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39, tzinfo=utc),
            dt.datetime(
                year=2021, month=5, day=26, hour=11, minute=39, second=1, tzinfo=utc
            ),
            dt.datetime(
                year=2021, month=5, day=26, hour=11, minute=40, second=1, tzinfo=utc
            ),
        ],
        [
            JobType.CYCLIC,
            dt.timedelta(hours=3, seconds=27),
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39),
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39)
            + dt.timedelta(hours=3, seconds=27),
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39)
            + 2 * dt.timedelta(hours=3, seconds=27),
        ],
    ),
)
def test_JobTimer_calc_next_exec(job_type, timing, start, target, next_target):
    timer = JobTimer(job_type, timing, start)

    timer.calc_next_exec()
    assert timer.datetime == target
    assert timer.timedelta(start) == target - start

    timer.calc_next_exec()
    assert timer.datetime == next_target


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

    jet = JobTimer(JobType.CYCLIC, delta, T_2021_5_26__3_55, True)
    assert jet.datetime == T_2021_5_26__3_55

    jet.calc_next_exec(T_2021_5_26__3_55 + offset)
    assert jet.datetime == T_2021_5_26__3_55 + res_delta


CYCLIC_TYPE_ERROR_MSG = (
    "Wrong input for Cyclic! Select one of the following input types:\n"
    + "datetime.timedelta | list[datetime.timedelta]"
)
_DAILY_TYPE_ERROR_MSG = (
    "Wrong input for {0}! Select one of the following input types:\n"
    + "datetime.time | list[datetime.time]"
)
MINUTELY_TYPE_ERROR_MSG = _DAILY_TYPE_ERROR_MSG.format("Minutely")
HOURLY_TYPE_ERROR_MSG = _DAILY_TYPE_ERROR_MSG.format("Hourly")
DAILY_TYPE_ERROR_MSG = _DAILY_TYPE_ERROR_MSG.format("Daily")
WEEKLY_TYPE_ERROR_MSG = (
    "Wrong input for Weekly! Select one of the following input types:\n"
    + "DAY | list[DAY]\n"
    + "where `DAY = Weekday | tuple[Weekday, dt.time]`"
)


@pytest.mark.parametrize(
    "job_type, timing, err",
    (
        [JobType.CYCLIC, dt.timedelta(), None],
        [JobType.CYCLIC, [dt.timedelta(), dt.timedelta()], None],
        [JobType.WEEKLY, Weekday.MONDAY, None],
        [JobType.DAILY, dt.time(), None],
        [JobType.DAILY, [dt.time(), dt.time()], None],
        [JobType.HOURLY, dt.time(), None],
        [JobType.HOURLY, [dt.time(), dt.time()], None],
        [JobType.MINUTELY, dt.time(), None],
        [JobType.MINUTELY, [dt.time(), dt.time()], None],
        [JobType.WEEKLY, (Weekday.MONDAY, dt.time()), None],
        [JobType.CYCLIC, (dt.timedelta(), dt.timedelta()), CYCLIC_TYPE_ERROR_MSG],
        [JobType.WEEKLY, dt.time(), WEEKLY_TYPE_ERROR_MSG],
        [JobType.WEEKLY, [Weekday.MONDAY, dt.time()], WEEKLY_TYPE_ERROR_MSG],
        [JobType.DAILY, (dt.time(), dt.time()), DAILY_TYPE_ERROR_MSG],
        [JobType.HOURLY, (dt.time(), dt.time()), HOURLY_TYPE_ERROR_MSG],
        [JobType.MINUTELY, (dt.time(), dt.time()), MINUTELY_TYPE_ERROR_MSG],
    ),
)
def test_sane_timing_types(job_type, timing, err):
    if err:
        with pytest.raises(SchedulerError, match=err):
            sane_timing_types(job_type, timing)
    else:
        sane_timing_types(job_type, timing)
