import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError
from scheduler.job import Job
from scheduler.util import Weekday

from helpers import (
    utc,
    CYCLIC_TYPE_ERROR_MSG,
    patch_datetime_now,
    samples_seconds,
    samples_days,
    foo,
)


@pytest.mark.parametrize(
    "timing, counts, patch_datetime_now, tzinfo, err_msg",
    (
        [dt.timedelta(seconds=4), [1, 2, 2, 2, 3, 3, 3], samples_seconds, None, None],
        [dt.timedelta(seconds=5), [1, 1, 2, 2, 2, 3, 3], samples_seconds, None, None],
        [dt.timedelta(seconds=5), [1, 1, 2, 2, 2, 3, 3], samples_seconds, utc, None],
        [dt.timedelta(days=2), [0, 0, 1, 2, 3, 4, 5], samples_days, None, None],
        [dt.time(hour=2), [], samples_days, None, CYCLIC_TYPE_ERROR_MSG],
        [Weekday.MONDAY, [], samples_days, None, CYCLIC_TYPE_ERROR_MSG],
    ),
    indirect=["patch_datetime_now"],
)
def test_cyclic(timing, counts, patch_datetime_now, tzinfo, err_msg):
    sch = Scheduler(tzinfo=tzinfo)

    if err_msg:
        with pytest.raises(SchedulerError) as err_msg:
            job = sch.cyclic(timing=timing, handle=foo)
    else:
        job = sch.cyclic(timing=timing, handle=foo)
        for count in counts:
            sch.exec_pending_jobs()
            assert job.attemps == count
