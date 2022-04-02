import datetime as dt

import pytest
from helpers import HOURLY_TYPE_ERROR_MSG, TZ_ERROR_MSG, foo, samples_hours, samples_hours_utc, utc

import scheduler.trigger as trigger
from scheduler import Scheduler, SchedulerError


@pytest.mark.parametrize(
    "timing, counts, patch_datetime_now, tzinfo, err_msg",
    (
        [dt.time(minute=0), [1, 2, 3, 4, 5, 6, 6], samples_hours, None, None],
        [dt.time(minute=39), [1, 2, 3, 4, 5, 5, 5], samples_hours, None, None],
        [
            [dt.time(minute=39), dt.time(hour=1, minute=39, tzinfo=utc)],
            [],
            samples_hours,
            None,
            TZ_ERROR_MSG,
        ],
        [
            dt.time(minute=47, tzinfo=utc),
            [1, 2, 3, 4, 5, 5, 5],
            samples_hours_utc,
            utc,
            None,
        ],
        [dt.time(hour=2), [], samples_hours_utc, utc, TZ_ERROR_MSG],
        [trigger.Monday(), [], samples_hours, None, HOURLY_TYPE_ERROR_MSG],
    ),
    indirect=["patch_datetime_now"],
)
def test_hourly(timing, counts, patch_datetime_now, tzinfo, err_msg):
    sch = Scheduler(tzinfo=tzinfo)

    if err_msg:
        with pytest.raises(SchedulerError) as msg:
            job = sch.hourly(timing=timing, handle=foo)
            assert msg == err_msg
    else:
        job = sch.hourly(timing=timing, handle=foo)
        attempts = []
        for _ in counts:
            sch.exec_jobs()
            attempts.append(job.attempts)
        assert attempts == counts
