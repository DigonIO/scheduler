from __future__ import annotations
import datetime as dt
from typing import Callable, Union, Tuple

from scheduler.job import Job
from scheduler.weekday import Weekday


class Oneshot(Job):
    def __init__(
        self,
        handle: Callable,
        weight: int = 1,
        t_delta: dt.timedelta = None,
        tw_stamp: Union[Weekday, dt.time, Tuple[Weekday, dt.time], None] = None,
        dt_stamp: dt.datetime = None,
    ):
        super().__init__(
            job_type=Job.Type.ONESHOT,
            handle=handle,
            weight=weight,
            max_attempts=1,
        )
