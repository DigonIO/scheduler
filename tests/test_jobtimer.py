import datetime as dt
from typing import Optional

import pytest

import scheduler.trigger as trigger
from scheduler import SchedulerError
from scheduler.base.definition import JobType
from scheduler.base.job_timer import JobTimer
from scheduler.base.job_util import sane_timing_types
from scheduler.base.timingtype import TimingJobTimerUnion, TimingJobUnion

from .helpers import CYCLIC_TYPE_ERROR_MSG, T_2021_5_26__3_55, utc


@pytest.mark.parametrize(
    "job_type, timing, start, target, next_target",
    (
        [
            JobType.WEEKLY,
            trigger.Thursday(),
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39, tzinfo=utc),
            dt.datetime(year=2021, month=5, day=27, tzinfo=utc),
            dt.datetime(year=2021, month=6, day=3, tzinfo=utc),
        ],
        [
            JobType.WEEKLY,
            trigger.Friday(dt.time(hour=1, minute=1, tzinfo=utc)),
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
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39, second=1, tzinfo=utc),
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=40, second=1, tzinfo=utc),
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
def test_JobTimer_calc_next_exec(
    job_type: JobType,
    timing: TimingJobTimerUnion,
    start: dt.datetime,
    target: dt.datetime,
    next_target: dt.datetime,
) -> None:
    timer = JobTimer(job_type, timing, start)

    assert timer.datetime == target
    assert timer.timedelta(start) == target - start

    timer.calc_next_exec()
    assert timer.datetime == next_target


@pytest.mark.parametrize(
    "delta_m, offset_m, skip, res_delta_m",
    (
        [20, 21, True, 41],
        [1, 21, True, 22],
        [1, 1, True, 2],
        [20, 20, True, 40],
        [20, 1, True, 21],
        [20, 21, False, 40],
        [1, 21, False, 2],
        [1, 1, False, 2],
        [20, 20, False, 40],
        [20, 1, False, 40],
    ),
)
def test_skip(delta_m: int, offset_m: int, skip: bool, res_delta_m: int) -> None:
    delta = dt.timedelta(minutes=delta_m)
    offset = dt.timedelta(minutes=offset_m)
    res_delta = dt.timedelta(minutes=res_delta_m)

    jet = JobTimer(
        JobType.CYCLIC,
        timing=delta,
        start=T_2021_5_26__3_55,
        skip_missing=skip,
    )
    assert jet.datetime == T_2021_5_26__3_55 + delta

    jet.calc_next_exec(T_2021_5_26__3_55 + offset)
    assert jet.datetime == T_2021_5_26__3_55 + res_delta


@pytest.mark.parametrize(
    "job_type, timing, err",
    (
        [JobType.CYCLIC, [dt.timedelta()], None],
        [JobType.CYCLIC, [dt.timedelta(), dt.timedelta()], CYCLIC_TYPE_ERROR_MSG],
        [JobType.WEEKLY, [trigger.Monday()], None],
        [JobType.DAILY, [dt.time()], None],
        [JobType.DAILY, [dt.time(), dt.time()], None],
        [JobType.HOURLY, [dt.time()], None],
        [JobType.HOURLY, [dt.time(), dt.time()], None],
        [JobType.MINUTELY, [dt.time()], None],
        [JobType.MINUTELY, [dt.time(), dt.time()], None],
        # [JobType.CYCLIC, (dt.timedelta(), dt.timedelta()), CYCLIC_TYPE_ERROR_MSG],
        # [JobType.WEEKLY, dt.time(), WEEKLY_TYPE_ERROR_MSG],
        # [JobType.WEEKLY, [trigger.Monday(), dt.time()], WEEKLY_TYPE_ERROR_MSG],
        # [JobType.DAILY, (dt.time(), dt.time()), DAILY_TYPE_ERROR_MSG],
        # [JobType.HOURLY, (dt.time(), dt.time()), HOURLY_TYPE_ERROR_MSG],
        # [JobType.MINUTELY, (dt.time(), dt.time()), MINUTELY_TYPE_ERROR_MSG],
    ),
)
def test_sane_timing_types(job_type: JobType, timing: TimingJobUnion, err: Optional[str]) -> None:
    if err:
        with pytest.raises(SchedulerError, match=err):
            sane_timing_types(job_type, timing)
    else:
        sane_timing_types(job_type, timing)
