"""
Implementation of essential `Job` components.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
from __future__ import annotations

import datetime as dt
import threading
from typing import Any, Optional, Union, cast

import typeguard as tg

from scheduler.base.definition import (
    JOB_NEXT_DAYLIKE_MAPPING,
    JOB_TIMING_TYPE_MAPPING,
    JobType,
)
from scheduler.error import SchedulerError
from scheduler.message import (
    _TZ_ERROR_MSG,
    DUPLICATE_EFFECTIVE_TIME,
    START_STOP_ERROR,
    TZ_ERROR_MSG,
)
from scheduler.timing_type import TimingJobTimerUnion, TimingJobUnion
from scheduler.trigger.core import Weekday
from scheduler.util import (
    are_times_unique,
    are_weekday_times_unique,
    next_weekday_time_occurrence,
)


class JobTimer:
    """
    The class provides the internal `datetime.datetime` calculations for a `Job`.

    Parameters
    ----------
    job_type : JobType
        Indicator which defines which calculations has to be used.
    timing : TimingJobTimerUnion
        Desired execution time(s).
    start : datetime.datetime
        Timestamp reference from which future executions will be calculated.
    skip_missing : bool
        If ``True`` a |Job| will only schedule it's newest planned
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
                    self.__next_exec = self.__next_exec.astimezone(
                        self.__timing.time.tzinfo
                    )
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
        return self.__next_exec - dt_stamp


@staticmethod
def get_pending_timer(timers: list[JobTimer]) -> JobTimer:
    """Get the the timer with the largest overdue time."""
    unsorted_timer_datetimes: dict[JobTimer, dt.datetime] = {}
    for timer in timers:
        unsorted_timer_datetimes[timer] = timer.datetime
    sorted_timers = sorted(
        unsorted_timer_datetimes,
        key=unsorted_timer_datetimes.get,  # type: ignore
    )
    return sorted_timers[0]


@staticmethod
def sane_timing_types(job_type: JobType, timing: TimingJobUnion) -> None:
    """
    Determine if the `JobType` is fulfilled by the type of the specified `timing`.
    Parameters
    ----------
    job_type : JobType
        :class:`~scheduler.job.JobType` to test agains.
    timing : TimingJobUnion
        The `timing` object to be tested.
    Raises
    ------
    TypeError
        If the `timing` object has the wrong `Type` for a specific `JobType`.
    """
    try:
        tg.check_type("timing", timing, JOB_TIMING_TYPE_MAPPING[job_type]["type"])
        if job_type == JobType.CYCLIC:
            if not len(timing) == 1:
                raise TypeError
    except TypeError as err:
        raise SchedulerError(JOB_TIMING_TYPE_MAPPING[job_type]["err"]) from err


@staticmethod
def standardize_timing_format(
    job_type: JobType, timing: TimingJobUnion
) -> TimingJobUnion:
    r"""
    Return timings in standarized form.
    Clears irrelevant time positionals for `JobType.MINUTELY` and `JobType.HOURLY`.
    """
    if job_type is JobType.MINUTELY:
        timing = [
            time.replace(hour=0, minute=0) for time in cast(list[dt.time], timing)
        ]
    elif job_type is JobType.HOURLY:
        timing = [time.replace(hour=0) for time in cast(list[dt.time], timing)]
    return timing


@staticmethod
def check_timing_tzinfo(
    job_type: JobType,
    timing: TimingJobUnion,
    tzinfo: Optional[dt.tzinfo],
):
    """Raise if `timing` incompatible with `tzinfo` for `job_type`."""
    if job_type is JobType.WEEKLY:
        for weekday in cast(list[Weekday], timing):
            if bool(weekday.time.tzinfo) ^ bool(tzinfo):
                raise SchedulerError(TZ_ERROR_MSG)
    elif job_type in (JobType.MINUTELY, JobType.HOURLY, JobType.DAILY):
        for time in cast(list[dt.time], timing):
            if bool(time.tzinfo) ^ bool(tzinfo):
                raise SchedulerError(TZ_ERROR_MSG)


@staticmethod
def check_duplicate_effective_timings(
    job_type: JobType,
    timing: TimingJobUnion,
    tzinfo: Optional[dt.tzinfo],
):
    """Raise given timings are not effectively duplicates."""
    if job_type is JobType.WEEKLY:
        if not are_weekday_times_unique(cast(list[Weekday], timing), tzinfo):
            raise SchedulerError(DUPLICATE_EFFECTIVE_TIME)
    elif job_type in (
        JobType.MINUTELY,
        JobType.HOURLY,
        JobType.DAILY,
    ):
        if not are_times_unique(cast(list[dt.time], timing)):
            raise SchedulerError(DUPLICATE_EFFECTIVE_TIME)


@staticmethod
def set_start_check_stop_tzinfo(
    start: Optional[dt.datetime],
    stop: Optional[dt.datetime],
    tzinfo: Optional[dt.tzinfo],
) -> dt.datetime:
    """Raise if `start`, `stop` and `tzinfo` incompatible; Make start."""
    if start:
        if bool(start.tzinfo) ^ bool(tzinfo):
            raise SchedulerError(_TZ_ERROR_MSG.format("start"))
    else:
        start = dt.datetime.now(tzinfo)
    if stop:
        if bool(stop.tzinfo) ^ bool(tzinfo):
            raise SchedulerError(_TZ_ERROR_MSG.format("stop"))
    if stop is not None:
        if start >= stop:
            raise SchedulerError(START_STOP_ERROR)
    return start
