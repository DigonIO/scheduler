"""
Collection of useful utility objects.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
from __future__ import annotations

import datetime as dt
import random
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Callable, Optional

from scheduler.trigger.core import Weekday

TZ_ERROR_MSG = "Can't use offset-naive and offset-aware datetimes together."


class SchedulerError(Exception):
    """Generic Scheduler exception."""


class JobType(Enum):
    """Indicate the `JobType` of a |Job|."""

    CYCLIC = auto()
    MINUTELY = auto()
    HOURLY = auto()
    DAILY = auto()
    WEEKLY = auto()


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


def are_weekday_times_unique(
    weekday_list: list[Weekday], tzinfo: Optional[dt.tzinfo]
) -> bool:
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


class AbstractJob(ABC):
    """
    Abstract definition of the `Job` class.

    Notes
    -----
    Needed to provide linting and typing in the :mod:`~scheduler.util` module.
    """

    @property
    @abstractmethod
    def type(self) -> JobType:
        """Return the `JobType` of the `Job` instance."""

    @property
    @abstractmethod
    def handle(self) -> Callable[..., None]:
        """Get the callback function handle."""

    @property
    @abstractmethod
    def kwargs(self) -> dict[str, Any]:
        r"""Get the payload arguments to pass to the function handle within a `Job`."""

    @property
    @abstractmethod
    def weight(self) -> float:
        """Return the weight of the `Job` instance."""

    @property
    @abstractmethod
    def delay(self) -> bool:
        """Return ``True`` if the first `Job` execution will wait for the next scheduled time."""

    @property
    @abstractmethod
    def start(self) -> Optional[dt.datetime]:
        """Get the timestamp at which the `JobTimer` starts."""

    @property
    @abstractmethod
    def stop(self) -> Optional[dt.datetime]:
        """Get the timestamp after which no more executions of the `Job` should be scheduled."""

    @property
    @abstractmethod
    def max_attempts(self) -> int:
        """Get the execution limit for a `Job`."""

    @property
    @abstractmethod
    def skip_missing(self) -> bool:
        """Return ``True`` if `Job` will only schedule it's newest planned execution."""

    @property
    @abstractmethod
    def tzinfo(self) -> Optional[dt.tzinfo]:
        r"""Get the timezone of the `Job`'s next execution."""

    @property
    @abstractmethod
    def _tzinfo(self) -> Optional[dt.tzinfo]:
        """Get the timezone of the `Scheduler` in which the `Job` is living."""

    @property
    @abstractmethod
    def has_attempts_remaining(self) -> bool:
        """Check if a `Job` has remaining attempts."""

    @property
    @abstractmethod
    def attempts(self) -> int:
        """Get the number of executions for a `Job`."""

    @property
    @abstractmethod
    def datetime(self) -> dt.datetime:
        """Give the `datetime.datetime` object for the planed execution."""

    @abstractmethod
    def timedelta(self, dt_stamp: Optional[dt.datetime] = None) -> dt.timedelta:
        """Get the `datetime.timedelta` until the next execution of this `Job`."""


class Prioritization:
    """
    Collection of prioritization functions.

    For compatibility with the |Scheduler|, the prioritization
    functions have to be of type ``Callable[[float, Job, int, int], float]``.
    """

    @staticmethod
    def constant_weight_prioritization(
        time_delta: float, job: AbstractJob, max_exec: int, job_count: int
    ) -> float:  # pragma: no cover
        r"""
        Interprete the `Job`'s weight as its priority.

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

    @staticmethod
    def linear_priority_function(
        time_delta: float, job: AbstractJob, max_exec: int, job_count: int
    ) -> float:
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

    @staticmethod
    def random_priority_function(
        time: float, job: AbstractJob, max_exec: int, job_count: int
    ) -> float:  # pragma: no cover
        """
        Generate random priority values from weigths.

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
        ``False`` for string abbreviation from the front, else ``True``.

    Returns
    -------
    str
        Resulting string
    """
    if max_length < 1:
        raise ValueError("max_length < 1 not allowed")

    if len(string) > max_length:
        pos = max_length - 1
        return string[:pos] + "#" if cut_tail else "#" + string[-pos:]

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
