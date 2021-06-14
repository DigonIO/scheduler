import datetime as dt

import pytest
from helpers import (
    T_2021_5_26__3_55,
    patch_datetime_now,
    samples,
    samples_once_datetime,
)

from scheduler import Scheduler, SchedulerError, Weekday

ERROR_MSG = (
    'Wrong input for "once"! Select one of the following input types:\n'
    + "dt.datetime, Weekday, dt.time, dt.timedelta, tuple[Weekday, dt.time]"
)


@pytest.mark.parametrize(
    "exec_at, exec_counts, patch_datetime_now, err_msg",
    (
        [dt.timedelta(seconds=5), [1, 1, 1, 1, 1, 1, 1], samples, None],
        [dt.timedelta(hours=1, minutes=1), [0, 0, 0, 1, 1, 1, 1], samples, None],
        [Weekday.THURSDAY, [0, 0, 0, 0, 0, 1, 1], samples, None],
        [dt.time(hour=3, minute=55, second=6), [0, 1, 1, 1, 1, 1, 1], samples, None],
        [
            (Weekday.THURSDAY, dt.time(hour=3, minute=55, second=6)),
            [0, 0, 0, 0, 0, 1, 1],
            samples,
            None,
        ],
        [234, [], samples, ERROR_MSG],
        [25.1, [], samples, ERROR_MSG],
        ["foo bar", [], samples, ERROR_MSG],
        [{Weekday.FRIDAY}, [], samples, ERROR_MSG],
    ),
    indirect=["patch_datetime_now"],
)
def test_once(patch_datetime_now, exec_at, exec_counts, err_msg):
    sch = Scheduler()
    if err_msg:
        with pytest.raises(SchedulerError) as err:
            sch.once(lambda: None, exec_at)
            assert ERROR_MSG == str(err.value)
    else:
        job = sch.once(lambda: None, exec_at)

        for count in exec_counts:
            sch.exec_jobs()
            assert job.attemps == count


@pytest.mark.parametrize(
    "exec_at, exec_counts, patch_datetime_now",
    (
        [
            T_2021_5_26__3_55 + dt.timedelta(seconds=6),
            [0, 1, 1, 1, 1],
            samples_once_datetime,
        ],
        [
            T_2021_5_26__3_55 + dt.timedelta(seconds=7),
            [0, 0, 1, 1, 1],
            samples_once_datetime,
        ],
        [
            T_2021_5_26__3_55 + dt.timedelta(seconds=8),
            [0, 0, 0, 1, 1],
            samples_once_datetime,
        ],
        [
            T_2021_5_26__3_55 + dt.timedelta(days=9, minutes=2),
            [0, 0, 0, 0, 0, 1, 1],
            samples_once_datetime,
        ],
    ),
    indirect=["patch_datetime_now"],
)
def test_once_with_datetime_over_schedule(exec_at, exec_counts, patch_datetime_now):
    sch = Scheduler()
    job = sch.schedule(
        lambda: None,
        dt.timedelta(seconds=1),
        delay=False,
        offset=exec_at,
        max_attempts=1,
    )

    assert job.datetime == exec_at

    for count in exec_counts:
        sch.exec_jobs()
        assert job.attemps == count
        assert job._has_attempts_remaining == (count == 0)

    assert job.datetime == exec_at + dt.timedelta(seconds=1)
