from __future__ import annotations
import datetime as dt
from typing import Callable, Union, Tuple, Sequence

from scheduler.job import Job
from scheduler.weekday import Weekday


class Routine(Job):
    def __init__(
        self,
        handle: Callable,
        weight: int = 1,
        t_delta: dt.timedelta = None,
        tw_stamps: Union[
            Sequence[Union[Weekday, dt.time, Tuple[Weekday, dt.time]]],
            Weekday,
            dt.time,
            Tuple[Weekday, dt.time],
            None,
        ] = None,
        max_attempts: int = 0,
    ):
        super().__init__(
            job_type=Job.Type.ROUTINE,
            handle=handle,
            weight=weight,
            max_attempts=max_attempts,
        )
