"""
Implementation of the essential timer for a `BaseJob`.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

from __future__ import annotations

import datetime as dt
import threading
from typing import Optional, cast

from scheduler.base.definition import JobType
from scheduler.base.timingtype import TimingJobTimerUnion
from scheduler.trigger.core import Weekday
from scheduler.util import JOB_NEXT_DAYLIKE_MAPPING, next_weekday_time_occurrence


class JobTimer:
    """
    The class provides the internal `datetime.datetime` calculations for a |BaseJob|.

    Parameters
    ----------
    job_type : JobType
        Indicator which defines which calculations has to be used.
    timing : TimingJobTimerUnion
        Desired execution time(s).
    start : datetime.datetime
        Timestamp reference from which future executions will be calculated.
    skip_missing : bool
        If ``True`` a |BaseJob| will only schedule it's newest planned
        execution and drop older ones.
    """

    def __init__(
        self,
        job_type: JobType,
        timing: TimingJobTimerUnion,
        start: dt.datetime,
        skip_missing: bool = False,
    ):
        self.__lock = threading.RLock()
        self.__job_type = job_type
        self.__timing = timing
        self.__next_exec = start
        self.__skip = skip_missing
        self.calc_next_exec()

    def calc_next_exec(self, ref: Optional[dt.datetime] = None) -> None:
        """
        Generate the next execution `datetime.datetime` stamp.

        Parameters
        ----------
        ref : Optional[datetime.datetime]
            Datetime reference for scheduling the next execution datetime.
        """
        with self.__lock:
            if self.__job_type == JobType.CYCLIC:
                if self.__skip and ref is not None:
                    self.__next_exec = ref
                self.__next_exec = self.__next_exec + cast(dt.timedelta, self.__timing)
                return

            if self.__job_type == JobType.WEEKLY:
                self.__timing = cast(Weekday, self.__timing)
                if self.__timing.time.tzinfo:
                    self.__next_exec = self.__next_exec.astimezone(self.__timing.time.tzinfo)
                self.__next_exec = next_weekday_time_occurrence(
                    self.__next_exec, self.__timing, self.__timing.time
                )

            else:  # self.__job_type in JOB_NEXT_DAYLIKE_MAPPING:
                self.__timing = cast(dt.time, self.__timing)
                if self.__next_exec.tzinfo:
                    self.__next_exec = self.__next_exec.astimezone(self.__timing.tzinfo)
                self.__next_exec = JOB_NEXT_DAYLIKE_MAPPING[self.__job_type](
                    self.__next_exec, self.__timing
                )

            if self.__skip and ref is not None and self.__next_exec < ref:
                self.__next_exec = ref
                self.calc_next_exec()

    @property
    def datetime(self) -> dt.datetime:
        """
        Get the `datetime.datetime` object for the planed execution.

        Returns
        -------
        datetime.datetime
            Execution `datetime.datetime` stamp.
        """
        with self.__lock:
            return self.__next_exec

    def timedelta(self, dt_stamp: dt.datetime) -> dt.timedelta:
        """
        Get the `datetime.timedelta` until the execution of this `Job`.

        Parameters
        ----------
        dt_stamp : datetime.datetime
            Time to be compared with the planned execution time
            to determine the time difference.

        Returns
        -------
        datetime.timedelta
            `datetime.timedelta` to the execution.
        """
        with self.__lock:
            return self.__next_exec - dt_stamp
