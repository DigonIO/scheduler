import datetime as dt

import pytest

import scheduler.trigger as trigger
from scheduler import Scheduler, SchedulerError

from ...helpers import CYCLIC_TYPE_ERROR_MSG, foo, samples_days, samples_seconds, utc


@pytest.mark.parametrize(
    "timing, counts, patch_datetime_now, tzinfo, err_msg",
    (
        [dt.timedelta(seconds=4), [1, 2, 2, 2, 3, 3, 3], samples_seconds, None, None],
        [dt.timedelta(seconds=5), [1, 1, 2, 2, 2, 3, 3], samples_seconds, None, None],
        [dt.timedelta(seconds=5), [1, 1, 2, 2, 2, 3, 3], samples_seconds, utc, None],
        [dt.timedelta(days=2), [0, 0, 1, 2, 2, 2, 2], samples_days, None, None],
        [dt.time(hour=2), [], samples_days, None, CYCLIC_TYPE_ERROR_MSG],
        [trigger.Monday(), [], samples_days, None, CYCLIC_TYPE_ERROR_MSG],
    ),
    indirect=["patch_datetime_now"],
)
def test_cyclic(timing, counts, patch_datetime_now, tzinfo, err_msg):
    sch = Scheduler(tzinfo=tzinfo)

    if err_msg:
        with pytest.raises(SchedulerError, match=err_msg):
            job = sch.cyclic(timing=timing, handle=foo)
    else:
        job = sch.cyclic(timing=timing, handle=foo)
        for count in counts:
            sch.exec_jobs()
            assert job.attempts == count
