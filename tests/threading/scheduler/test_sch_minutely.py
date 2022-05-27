import datetime as dt

import pytest
from ...helpers import (
    DUPLICATE_EFFECTIVE_TIME,
    MINUTELY_TYPE_ERROR_MSG,
    TZ_ERROR_MSG,
    foo,
    samples_half_minutes,
    samples_minutes,
    samples_minutes_utc,
    utc,
)

import scheduler.trigger as trigger
from scheduler import Scheduler, SchedulerError


@pytest.mark.parametrize(
    "timing, counts, patch_datetime_now, tzinfo, err_msg",
    (
        [dt.time(second=0), [1, 2, 3, 4, 5, 5, 5], samples_minutes, None, None],
        [dt.time(second=39), [1, 2, 3, 4, 5, 6, 6], samples_minutes, None, None],
        [
            [dt.time(second=5), dt.time(second=30)],
            [1, 1, 2, 3, 4, 4, 5, 6, 7],
            samples_half_minutes,
            None,
            None,
        ],
        [
            [dt.time(second=5), dt.time(minute=1, second=5)],
            [],
            samples_half_minutes,
            None,
            DUPLICATE_EFFECTIVE_TIME,
        ],
        [
            dt.time(second=47, tzinfo=utc),
            [1, 2, 3, 4, 5, 5, 5],
            samples_minutes_utc,
            utc,
            None,
        ],
        [dt.time(hour=2), [], samples_minutes_utc, utc, TZ_ERROR_MSG],
        [trigger.Monday(), [], samples_minutes, None, MINUTELY_TYPE_ERROR_MSG],
    ),
    indirect=["patch_datetime_now"],
)
def test_minutely(timing, counts, patch_datetime_now, tzinfo, err_msg):
    sch = Scheduler(tzinfo=tzinfo)

    if err_msg:
        with pytest.raises(SchedulerError) as msg:
            job = sch.minutely(timing=timing, handle=foo)
            assert msg == err_msg
    else:
        job = sch.minutely(timing=timing, handle=foo)
        attempts = []
        for _ in counts:
            sch.exec_jobs()
            attempts.append(job.attempts)
        assert attempts == counts
