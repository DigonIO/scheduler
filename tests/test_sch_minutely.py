import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.job import Job
from scheduler.util import Weekday

from helpers import (
    utc,
    MINUTELY_TYPE_ERROR_MSG,
    TZ_ERROR_MSG,
    samples_minutes,
    samples_minutes_utc,
    foo,
)


@pytest.mark.parametrize(
    "timing, counts, patch_datetime_now, tzinfo, err_msg",
    (
        [dt.time(second=0), [1, 2, 3, 4, 5, 5, 5], samples_minutes, None, None],
        [dt.time(second=39), [1, 2, 3, 4, 5, 6, 6], samples_minutes, None, None],
        [
            dt.time(second=47, tzinfo=utc),
            [1, 2, 3, 4, 5, 5, 5],
            samples_minutes_utc,
            utc,
            None,
        ],
        [dt.time(hour=2), [], samples_minutes_utc, utc, TZ_ERROR_MSG],
        [Weekday.MONDAY, [], samples_minutes, None, MINUTELY_TYPE_ERROR_MSG],
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
        for count in counts:
            sch.exec_jobs()
            assert job.attemps == count
