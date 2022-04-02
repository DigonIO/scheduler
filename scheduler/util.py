"""
Collection of datetime and trigger related utility functions.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
from __future__ import annotations

import datetime as dt
import random
import warnings
from typing import Callable, Optional

from scheduler.base.definition import JobType
from scheduler.error import SchedulerError
from scheduler.trigger.core import Weekday


def days_to_weekday(wkdy_src: int, wkdy_dest: int) -> int:
    """
    Calculate the days to a specific destination weekday.

    Notes
    -----
    Weekday enumeration based on
    the `datetime` standard library.

    Parameters
    ----------
    wkdy_src : int
        Source :class:`~scheduler.util.Weekday` integer representation.
    wkdy_dest : int
        Destination :class:`~scheduler.util.Weekday` interger representation.

    Returns
    -------
    int
        Days to the destination :class:`~scheduler.util.Weekday`.
    """
    if not (0 <= wkdy_src <= 6 and 0 <= wkdy_dest <= 6):
        raise SchedulerError("Weekday enumeration interval: [0,6] <=> [Monday, Sunday]")

    return (wkdy_dest - wkdy_src - 1) % 7 + 1


def next_daily_occurrence(now: dt.datetime, target_time: dt.time) -> dt.datetime:
    """
    Estimate the next daily occurency of a given time.

    .. warning:: Both arguments are expected to have the same tzinfo, no internal checks.

    Parameters
    ----------
    now : datetime.datetime
        `datetime.datetime` object of today
    target_time : datetime.time
        Desired `datetime.time`.

    Returns
    -------
    datetime.datetime
        Next `datetime.datetime` object with the desired time.
    """
    target = now.replace(
        hour=target_time.hour,
        minute=target_time.minute,
        second=target_time.second,
        microsecond=target_time.microsecond,
    )
    if (target - now).total_seconds() <= 0:
        target = target + dt.timedelta(days=1)
    return target


def next_hourly_occurrence(now: dt.datetime, target_time: dt.time) -> dt.datetime:
    """
    Estimate the next hourly occurency of a given time.

    .. warning:: Both arguments are expected to have the same tzinfo, no internal checks.

    Parameters
    ----------
    now : datetime.datetime
        `datetime.datetime` object of today
    target_time : datetime.time
        Desired `datetime.time`.

    Returns
    -------
    datetime.datetime
        Next `datetime.datetime` object with the desired time.
    """
    target = now.replace(
        minute=target_time.minute,
        second=target_time.second,
        microsecond=target_time.microsecond,
    )
    if (target - now).total_seconds() <= 0:
        target = target + dt.timedelta(hours=1)
    return target


def next_minutely_occurrence(now: dt.datetime, target_time: dt.time) -> dt.datetime:
    """
    Estimate the next weekly occurency of a given time.

    .. warning:: Both arguments are expected to have the same tzinfo, no internal checks.

    Parameters
    ----------
    now : datetime.datetime
        `datetime.datetime` object of today
    target_time : datetime.time
        Desired `datetime.time`.

    Returns
    -------
    datetime.datetime
        Next `datetime.datetime` object with the desired time.
    """
    target = now.replace(
        second=target_time.second,
        microsecond=target_time.microsecond,
    )
    if (target - now).total_seconds() <= 0:
        return target + dt.timedelta(minutes=1)
    return target


def next_weekday_time_occurrence(
    now: dt.datetime, weekday: Weekday, target_time: dt.time
) -> dt.datetime:
    """
    Estimate the next occurency of a given weekday and time.

    .. warning:: Arguments `now` and `target_time` are expected to have the same tzinfo,
       no internal checks.

    Parameters
    ----------
    now : datetime.datetime
        `datetime.datetime` object of today
    weekday : Weekday
        Desired :class:`~scheduler.util.Weekday`.
    target_time : datetime.time
        Desired `datetime.time`.

    Returns
    -------
    datetime.datetime
        Next `datetime.datetime` object with the desired weekday and time.
    """
    days = days_to_weekday(now.weekday(), weekday.value)
    if days == 7:
        candidate = next_daily_occurrence(now, target_time)
        if candidate.date() == now.date():
            return candidate

    delta = dt.timedelta(days=days)
    target = now.replace(
        hour=target_time.hour,
        minute=target_time.minute,
        second=target_time.second,
        microsecond=target_time.microsecond,
    )
    return target + delta


JOB_NEXT_DAYLIKE_MAPPING = {
    JobType.MINUTELY: next_minutely_occurrence,
    JobType.HOURLY: next_hourly_occurrence,
    JobType.DAILY: next_daily_occurrence,
}


def are_times_unique(
    timelist: list[dt.time],
) -> bool:
    r"""
    Check if list contains distinct `datetime.time`\ s.

    Parameters
    ----------
    timelist : list[datetime.time]
        List of time objects.

    Returns
    -------
    boolean
        ``True`` if list entries are not equivalent with tzinfo offset.
    """
    ref = dt.datetime(year=1970, month=1, day=1)
    collection = {
        ref.replace(
            hour=time.hour,
            minute=time.minute,
            second=time.second,
            microsecond=time.microsecond,
        )
        + (time.utcoffset() or dt.timedelta())
        for time in timelist
    }
    return len(collection) == len(timelist)


def are_weekday_times_unique(weekday_list: list[Weekday], tzinfo: Optional[dt.tzinfo]) -> bool:
    """
    Check if list contains distinct weekday times.

    .. warning:: Both arguments are expected to be either timezone aware or not
        - no internal checks.

    Parameters
    ----------
    weekday_list : list[Weekday]
        List of weekday objects.

    Returns
    -------
    boolean
        ``True`` if list entries are not equivalent with timezone offset.
    """
    ref = dt.datetime(year=1970, month=1, day=1, tzinfo=tzinfo)
    collection = {
        next_weekday_time_occurrence(ref.astimezone(day.time.tzinfo), day, day.time)
        for day in weekday_list
    }
    return len(collection) == len(weekday_list)


# NOTE: will be removed in next minor release (0.8.0)
def _constant_weight_prioritization(
    time_delta: float, job: Job, max_exec: int, job_count: int
) -> float:
    r"""
    Interprets the `Job`'s weight as its priority.

    Return the |Job|'s weight for overdue
    |Job|\ s, otherwise return zero:

    .. math::
        \left(\mathtt{time\_delta},\mathtt{weight}\right)\ {\mapsto}\begin{cases}
        0 & :\ \mathtt{time\_delta}<0\\
        \mathtt{weight} & :\ \mathtt{time\_delta}\geq0
        \end{cases}

    Parameters
    ----------
    time_delta : float
        The time in seconds that a |Job| is overdue.
    job : Job
        The |Job| instance
    max_exec : int
        Limits the number of overdue |Job|\ s that can be executed
        by calling function `Scheduler.exec_jobs()`.
    job_count : int
        Number of scheduled |Job|\ s

    Returns
    -------
    float
        The weight of a |Job| as priority.
    """
    _ = max_exec
    _ = job_count
    if time_delta < 0:
        return 0
    return job.weight


# NOTE: will be removed in next minor release (0.8.0)
def _linear_priority_function(time_delta: float, job: Job, max_exec: int, job_count: int) -> float:
    r"""
    Compute the |Job|\ s default linear priority.

    Linear |Job| prioritization such that the priority increases
    linearly with the amount of time that a |Job| is overdue.
    At the exact time of the scheduled execution, the priority is equal to the
    |Job|\ s weight.

    The function is defined as

    .. math::
        \left(\mathtt{time\_delta},\mathtt{weight}\right)\ {\mapsto}\begin{cases}
        0 & :\ \mathtt{time\_delta}<0\\
        {\left(\mathtt{time\_delta}+1\right)}\cdot\mathtt{weight} & :\ \mathtt{time\_delta}\geq0
        \end{cases}

    Parameters
    ----------
    time_delta : float
        The time in seconds that a |Job| is overdue.
    job : Job
        The |Job| instance
    max_exec : int
        Limits the number of overdue |Job|\ s that can be executed
        by calling function `Scheduler.exec_jobs()`.
    job_count : int
        Number of scheduled |Job|\ s

    Returns
    -------
    float
        The time dependant priority for a |Job|
    """
    _ = max_exec
    _ = job_count

    if time_delta < 0:
        return 0
    return (time_delta + 1) * job.weight


# NOTE: will be removed in next minor release (0.8.0)
def _random_priority_function(time: float, job: Job, max_exec: int, job_count: int) -> float:
    """
    Generate random priority values from weights.

    .. warning:: Not suitable for security relevant purposes.

    The priority generator will return 1 if the random number
    is lower then the |Job|'s weight, otherwise it will return 0.
    """
    _ = time
    _ = max_exec
    _ = job_count
    if random.random() < job.weight:  # nosec
        return 1
    return 0


def _warn_deprecated(
    function: Callable[[float, Job, int, int], float]
) -> Callable[[float, Job, int, int], float]:
    def wrapped_function(time: float, job: Job, max_exec: int, job_count: int) -> float:
        warnings.warn(
            (
                "Deprecated import! Use scheduler.prioritization instead of "
                "scheduler.util.Prioritization."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        return function(time, job, max_exec, job_count)

    return wrapped_function


# NOTE: will be removed in next minor release (0.8.0)
class Prioritization:
    """
    Collection of prioritization functions.

    For compatibility with the |Scheduler|, the prioritization
    functions have to be of type ``Callable[[float, Job, int, int], float]``.
    """

    constant_weight_prioritization = _warn_deprecated(_constant_weight_prioritization)
    linear_priority_function = _warn_deprecated(_linear_priority_function)
    random_priority_function = _warn_deprecated(_random_priority_function)
