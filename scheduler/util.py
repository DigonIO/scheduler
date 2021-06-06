"""
Collection of useful utility objects.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
import datetime as dt
from enum import Enum


class SchedulerError(Exception):
    """Generic `Scheduler` exception implementation."""


class Weekday(Enum):
    """
    Enum representation of weekdays.

    Notes
    -----
    The `Weekday` enumeration is based on the numeration of
    weekdays in the `datetime` standard library.
    """

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


def days_to_weekday(wkdy_src: int, wkdy_dest: int) -> int:
    """
    Calculate the days to a specific destination weekday.

    Notes
    -----
    Weekday numeration based on
    the `datetime` standard library.

    Parameters
    ----------
    wkdy_src : int
        Source `Weekday` integer representation.
    wkdy_dest : int
        Destination `Weekday` interger representation.

    Returns
    -------
    int
        Days to the destination weekday.
    """
    if wkdy_src > 6 or wkdy_src < 0 or wkdy_dest > 6 or wkdy_dest < 0:
        raise SchedulerError("Weekday enumeration interval: [0,6] <=> [Monday, Sunday]")

    if wkdy_src == wkdy_dest:
        return 7
    if wkdy_dest < wkdy_src:
        return 7 - wkdy_src + wkdy_dest
    return wkdy_dest - wkdy_src


def next_weekday_occurrence(now: dt.datetime, weekday: Weekday) -> dt.datetime:
    """
    Estimate the next occurency of a given `Weekday`.

    Parameters
    ----------
    now : datetime.datetime
        `datetime.datetime` object of today
    weekday : Weekday
        Desired `Weekday`.

    Returns
    -------
    datetime.datetime
        Next `datetime.datetime` of a desired `Weekday`.
    """
    days = days_to_weekday(now.weekday(), weekday.value)
    delta = dt.timedelta(days=days)
    target = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return target + delta


def next_time_occurrence(now: dt.datetime, target_time: dt.time) -> dt.datetime:
    """
    Estimate the next occurency of a given time.

    Parameters
    ----------
    now : datetime.datetime
        `datetime.datetime` object of today
    target_time : datetime.time
        Desired time.

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


def next_weekday_time_occurrence(
    now: dt.datetime, weekday: Weekday, target_time: dt.time
) -> dt.datetime:
    """
    Estimate the next occurency of a given weekday and time.

    Parameters
    ----------
    now : datetime.datetime
        `datetime.datetime` object of today
    weekday : Weekday
        Desired `Weekday`.
    target_time : datetime.time
        Desired time.

    Returns
    -------
    datetime.datetime
        Next `datetime.datetime` object with the desired `Weekday` and time.
    """
    days = days_to_weekday(now.weekday(), weekday.value)
    delta = dt.timedelta(days=days)
    target = now.replace(
        hour=target_time.hour,
        minute=target_time.minute,
        second=target_time.second,
        microsecond=target_time.microsecond,
    )
    return target + delta


class Job:
    """Forward declaration."""


def linear_weight_function(seconds: float, job: Job, **kwargs) -> float:
    """
    Compute the default linear weights.

    Linear `Job` weighting such that the effective weight increases linearly with
    the amount of time that a `Job` is overdue. At the exact time of the desired
    execution, the effective weight becomes the given weight of the `Job`.

    Parameters
    ----------
    seconds : float
        The time in seconds that a `Job` is overdue.
    job : Job
        The `Job` instance

    Returns
    -------
    float
        The time dependant effective weight for a `Job`
    """
    if seconds < 0:
        return 0
    return (seconds + 1) * job.weight
