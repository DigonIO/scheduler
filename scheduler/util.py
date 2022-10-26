"""
Collection of datetime and trigger related utility functions.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

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
        Destination :class:`~scheduler.util.Weekday` integer representation.

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
    Estimate the next daily occurrence of a given time.

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
    Estimate the next hourly occurrence of a given time.

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
    Estimate the next weekly occurrence of a given time.

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
    Estimate the next occurrence of a given weekday and time.

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
