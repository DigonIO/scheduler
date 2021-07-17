import datetime as dt

import pytest
from helpers import CYCLIC_TYPE_ERROR_MSG, T_2021_5_26__3_55, utc

from scheduler import SchedulerError
from scheduler.job import JobTimer, JobType, JobUtil
from scheduler.trigger import Trigger


@pytest.mark.parametrize(
    "job_type, timing, start, target, next_target",
    (
        [
            JobType.WEEKLY,
            Trigger.Weekly.Thursday(),
            dt.datetime(year=2021, month=5, day=26, hour=11, minute=39, tzinfo=utc),
            dt.datetime(year=2021, month=5, day=27, tzinfo=utc),
            dt.datetime(year=2021, month=6, day=3, tzinfo=utc),
        ],
        [
            JobType.WEEKLY,
            Trigger.Weekly.Friday(dt.time(hour=1, minute=1, tzinfo=utc)),
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
def test_skip(delta_m, offset_m, skip, res_delta_m):
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
        [JobType.WEEKLY, [Trigger.Weekly.Monday()], None],
        [JobType.DAILY, [dt.time()], None],
        [JobType.DAILY, [dt.time(), dt.time()], None],
        [JobType.HOURLY, [dt.time()], None],
        [JobType.HOURLY, [dt.time(), dt.time()], None],
        [JobType.MINUTELY, [dt.time()], None],
        [JobType.MINUTELY, [dt.time(), dt.time()], None],
        # [JobType.CYCLIC, (dt.timedelta(), dt.timedelta()), CYCLIC_TYPE_ERROR_MSG],
        # [JobType.WEEKLY, dt.time(), WEEKLY_TYPE_ERROR_MSG],
        # [JobType.WEEKLY, [Trigger.Weekly.Monday(), dt.time()], WEEKLY_TYPE_ERROR_MSG],
        # [JobType.DAILY, (dt.time(), dt.time()), DAILY_TYPE_ERROR_MSG],
        # [JobType.HOURLY, (dt.time(), dt.time()), HOURLY_TYPE_ERROR_MSG],
        # [JobType.MINUTELY, (dt.time(), dt.time()), MINUTELY_TYPE_ERROR_MSG],
    ),
)
def test_sane_timing_types(job_type, timing, err):
    if err:
        with pytest.raises(SchedulerError, match=err):
            JobUtil.sane_timing_types(job_type, timing)
    else:
        JobUtil.sane_timing_types(job_type, timing)
