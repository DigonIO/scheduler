"""
Implementation of essential functions for a `BaseJob`.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

from __future__ import annotations

import datetime as dt
from typing import Optional, cast

import typeguard as tg

from scheduler.base.definition import JOB_TIMING_TYPE_MAPPING, JobType
from scheduler.base.job_timer import JobTimer
from scheduler.base.timingtype import TimingJobUnion
from scheduler.error import SchedulerError
from scheduler.message import (
    _TZ_ERROR_MSG,
    DUPLICATE_EFFECTIVE_TIME,
    START_STOP_ERROR,
    TZ_ERROR_MSG,
)
from scheduler.trigger.core import Weekday
from scheduler.util import are_times_unique, are_weekday_times_unique


def prettify_timedelta(timedelta: dt.timedelta) -> str:
    """
    Humanize timedelta string readability for negative values.

    Parameters
    ----------
    timedelta : datetime.timedelta
        datetime instance

    Returns
    -------
    str
        Human readable string representation rounded to seconds
    """
    seconds = timedelta.total_seconds()
    if seconds < 0:
        res = f"-{-timedelta}"
    else:
        res = str(timedelta)
    return res.split(",")[0].split(".")[0]


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
        tg.check_type(timing, JOB_TIMING_TYPE_MAPPING[job_type]["type"])
        if job_type == JobType.CYCLIC:
            if not len(timing) == 1:
                raise TypeError
    except TypeError as err:
        raise SchedulerError(JOB_TIMING_TYPE_MAPPING[job_type]["err"]) from err


def standardize_timing_format(job_type: JobType, timing: TimingJobUnion) -> TimingJobUnion:
    r"""
    Return timings in standardized form.

    Clears irrelevant time positionals for `JobType.MINUTELY` and `JobType.HOURLY`.
    """
    if job_type is JobType.MINUTELY:
        timing = [time.replace(hour=0, minute=0) for time in cast(list[dt.time], timing)]
    elif job_type is JobType.HOURLY:
        timing = [time.replace(hour=0) for time in cast(list[dt.time], timing)]
    return timing


def check_timing_tzinfo(
    job_type: JobType,
    timing: TimingJobUnion,
    tzinfo: Optional[dt.tzinfo],
) -> None:
    """Raise if `timing` incompatible with `tzinfo` for `job_type`."""
    if job_type is JobType.WEEKLY:
        for weekday in cast(list[Weekday], timing):
            if bool(weekday.time.tzinfo) ^ bool(tzinfo):
                raise SchedulerError(TZ_ERROR_MSG)
    elif job_type in (JobType.MINUTELY, JobType.HOURLY, JobType.DAILY):
        for time in cast(list[dt.time], timing):
            if bool(time.tzinfo) ^ bool(tzinfo):
                raise SchedulerError(TZ_ERROR_MSG)


def check_duplicate_effective_timings(
    job_type: JobType,
    timing: TimingJobUnion,
    tzinfo: Optional[dt.tzinfo],
) -> None:
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
