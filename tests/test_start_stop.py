import datetime as dt

import pytest

from scheduler import Scheduler, SchedulerError

from helpers import (
    START_STOP_ERROR,
    samples_seconds,
    foo,
)

# Attention: t1 will be the second datetime object in the sample
# because with start the Job do not require a dt.datetime.now() in its init
# So we consume it with a _


@pytest.mark.parametrize(
    "timing, counts, patch_datetime_now, start, stop, err_msg",
    (
        [
            dt.timedelta(seconds=4),
            [],
            samples_seconds,
            dt.datetime(2021, 5, 26, 3, 55),
            dt.datetime(2021, 5, 26, 3, 55),
            START_STOP_ERROR,
        ],
        [
            dt.timedelta(seconds=2.75),
            [0, 1, 2, 2, 2, 2],
            samples_seconds,
            dt.datetime(2021, 5, 26, 3, 55, 5),
            dt.datetime(2021, 5, 26, 3, 55, 13),
            None,
        ],
        [
            dt.timedelta(seconds=3),
            [0, 1, 2, 2, 2, 2],
            samples_seconds,
            dt.datetime(2021, 5, 26, 3, 55, 5),
            dt.datetime(2021, 5, 26, 3, 55, 13),
            None,
        ],
        [
            dt.timedelta(seconds=5),
            [1, 1, 2, 2, 2, 2, 2, 2],
            samples_seconds,
            dt.datetime(2021, 5, 26, 3, 55, 0),
            dt.datetime(2021, 5, 26, 3, 55, 14),
            None,
        ],
        [
            dt.timedelta(seconds=5),
            [1, 1, 2, 2, 2, 3, 3, 3],
            samples_seconds,
            dt.datetime(2021, 5, 26, 3, 55, 0),
            dt.datetime(2021, 5, 26, 3, 55, 15),
            None,
        ],
        [
            dt.timedelta(seconds=5),
            [0, 0, 0],
            samples_seconds,
            None,
            dt.datetime(2021, 5, 26, 3, 54),
            None,
        ],
    ),
    indirect=["patch_datetime_now"],
)
def test_start_stop(timing, counts, patch_datetime_now, start, stop, err_msg):
    sch = Scheduler()

    _ = dt.datetime.now()

    if err_msg:
        with pytest.raises(SchedulerError) as msg:
            job = sch.cyclic(timing=timing, handle=foo, start=start, stop=stop)
            assert msg == err_msg
    else:
        job = sch.cyclic(timing=timing, handle=foo, start=start, stop=stop)

        if start is not None:
            assert job.start == start
        assert job.stop == stop

        for count in counts:
            sch.exec_jobs()
            assert job.attemps == count
