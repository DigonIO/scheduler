import pytest
import datetime as dt

from scheduler.util import (
    SchedulerError,
    Weekday,
)
from scheduler.job import JobExecTimer


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
