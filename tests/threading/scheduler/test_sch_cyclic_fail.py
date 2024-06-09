import datetime as dt
import logging
from typing import Any

import pytest

from scheduler import Scheduler

from ...helpers import fail, samples_seconds


@pytest.mark.parametrize(
    "timing, counts, patch_datetime_now",
    ([dt.timedelta(seconds=4), [1, 2], samples_seconds],),
    indirect=["patch_datetime_now"],
)
def test_threading_fail(
    timing: dt.timedelta,
    counts: list[int],
    patch_datetime_now: Any,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.DEBUG, logger="scheduler")

    sch = Scheduler()
    job = sch.cyclic(timing=timing, handle=fail)
    RECORD = (
        "scheduler",
        logging.ERROR,
        "Unhandled exception in `%r`!" % (job,),
    )

    for count in counts:
        sch.exec_jobs()
        assert job.attempts == count
        assert job.failed_attempts == count

    assert caplog.record_tuples == [RECORD, RECORD]
