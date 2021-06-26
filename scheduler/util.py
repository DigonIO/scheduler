"""
Collection of useful utility objects.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
from __future__ import annotations
import datetime as dt
from enum import Enum
from abc import ABC, abstractproperty


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


def next_daily_occurrence(now: dt.datetime, target_time: dt.time) -> dt.datetime:
    """
    Estimate the next daily occurency of a given time.

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


def next_hourly_occurrence(now: dt.datetime, target_time: dt.time) -> dt.datetime:
    """
    Estimate the next hourly occurency of a given time.

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
        second=target_time.second,
        microsecond=target_time.microsecond,
    )
    if (target - now).total_seconds() <= 0:
        target = target + dt.timedelta(minutes=1)
    return target


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


class AbstractJob(ABC):
    """
    Abstract definition of the `Job` class.

    Notes
    -----
    Needed to provide linting and typing in the `scheduler.util.py` module.
    """

    @abstractproperty
    def weight(self) -> float:
        """Abstract weight."""


def linear_priority_function(
    seconds: float, job: AbstractJob, max_exec: int, job_count: int
) -> float:
    r"""
    Compute the `Job`\ s default linear priority.

    Linear `Job` prioritization such that the priority increases linearly with
    the amount of time that a `Job` is overdue. At the exact time of the scheduled
    execution, the priority is equal to the `Job`\ s weight.

    Parameters
    ----------
    seconds : float
        The time in seconds that a `Job` is overdue.
    job : Job
        The `Job` instance
    _max_exec : int
        Limits the number of overdue `Job`\ s that can be executed
        by calling function `Scheduler.exec_jobs()`.
    _job_count : int
        Number of scheduled `Job`\ s

    Returns
    -------
    float
        The time dependant priority for a `Job`
    """
    _ = max_exec
    _ = job_count

    if seconds < 0:
        return 0
    return (seconds + 1) * job.weight


def str_cutoff(string: str, max_length: int, cut_tail: bool = False) -> str:
    """
    Abbreviate a string to a given length.

    The resulting string will carry an indicator if it's abbreviated,
    like ``stri#``.

    Parameters
    ----------
    string : str
        String which is to be cut.
    max_length : int
        Max resulting string length.
    cut_tail : bool
        `False` for string abbreviation from the front, else `True`.

    Returns
    -------
    str
        Resulting string
    """
    if max_length < 1:
        raise ValueError("max_length < 1 not allowed")

    if len(string) > max_length:
        pos = max_length - 1
        if cut_tail:
            return string[:pos] + "#"
        return "#" + string[-pos:]
    return string


def prettify_timedelta(timedelta: dt.timedelta) -> str:
    """
    Humanize timedelta string readibility for negative values.

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
