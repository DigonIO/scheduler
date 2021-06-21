import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.job import Job
from scheduler.util import Weekday

from helpers import (
    utc,
    DAILY_TYPE_ERROR_MSG,
    TZ_ERROR_MSG,
    samples_days,
    samples_days_utc,
    foo,
)


@pytest.mark.parametrize(
    "timing, counts, patch_datetime_now, tzinfo, err_msg",
    (
        [
            dt.time(hour=4, minute=30),
            [1, 2, 3, 4, 5, 6, 6, 6],
            samples_days,
            None,
            None,
        ],
        [
            dt.time(hour=16, minute=45),
            [1, 1, 2, 3, 4, 5, 6, 6],
            samples_days,
            None,
            None,
        ],
        [
            dt.time(hour=14, tzinfo=utc),
            [1, 1, 2, 3, 4, 5, 6, 6],
            samples_days_utc,
            utc,
            None,
        ],
        [dt.time(hour=2), [], samples_days_utc, utc, TZ_ERROR_MSG],
        [Weekday.MONDAY, [], samples_days, None, DAILY_TYPE_ERROR_MSG],
    ),
    indirect=["patch_datetime_now"],
)
def test_daily(timing, counts, patch_datetime_now, tzinfo, err_msg):
    sch = Scheduler(tzinfo=tzinfo)

    if err_msg:
        with pytest.raises(SchedulerError) as msg:
            job = sch.daily(timing=timing, handle=foo)
            assert msg == err_msg
    else:
        job = sch.daily(timing=timing, handle=foo)
        for count in counts:
            sch.exec_jobs()
            assert job.attemps == count
