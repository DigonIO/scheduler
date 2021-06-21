import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.job import Job
from scheduler.util import Weekday

from helpers import (
    utc,
    WEEKLY_TYPE_ERROR_MSG,
    TZ_ERROR_MSG,
    samples_weeks,
    samples_weeks_utc,
    foo,
)


@pytest.mark.parametrize(
    "timing, counts, patch_datetime_now, tzinfo, err_msg",
    (
        [
            Weekday.FRIDAY,
            [1, 2, 2, 2, 3, 3, 4, 4],
            samples_weeks,
            None,
            None,
        ],
        [
            (Weekday.FRIDAY, dt.time(hour=4, tzinfo=utc)),
            [1, 1, 2, 2, 2, 3, 3, 4],
            samples_weeks_utc,
            None,
            None,
        ],
        [
            Weekday.SUNDAY,
            [1, 1, 1, 2, 2, 3, 3, 3],
            samples_weeks,
            None,
            None,
        ],
        [
            [Weekday.WEDNESDAY, Weekday.SUNDAY],
            [1, 2, 2, 3, 4, 5, 6, 6],
            samples_weeks_utc,
            None,
            None,
        ],
        [
            [
                (Weekday.FRIDAY, dt.time(hour=4, tzinfo=utc)),
                (Weekday.FRIDAY, dt.time(hour=4, tzinfo=None)),
            ],
            [],
            samples_weeks_utc,
            utc,
            TZ_ERROR_MSG,
        ],
        [dt.time(), [], samples_weeks, None, WEEKLY_TYPE_ERROR_MSG],
        [dt.timedelta(), [], samples_weeks, None, WEEKLY_TYPE_ERROR_MSG],
    ),
    indirect=["patch_datetime_now"],
)
def test_weekly(timing, counts, patch_datetime_now, tzinfo, err_msg):
    sch = Scheduler(tzinfo=tzinfo)

    if err_msg:
        with pytest.raises(SchedulerError) as msg:
            job = sch.weekly(timing=timing, handle=foo)
            assert msg == err_msg
    else:
        job = sch.weekly(timing=timing, handle=foo)
        for count in counts:
            sch.exec_jobs()
            assert job.attemps == count
