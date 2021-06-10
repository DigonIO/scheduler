"""
Implementation of a `Job` as callback function represention.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
from __future__ import annotations

import datetime as dt
from typing import Callable, Optional, Union, Any

import typeguard as tg

from scheduler.util import (
    SchedulerError,
    Weekday,
    next_time_occurrence,
    next_weekday_occurrence,
    next_weekday_time_occurrence,
)

# execution time stamp typing for a cyclic Job
TimeTypes = Union[Weekday, dt.time, dt.timedelta, tuple[Weekday, dt.time]]
ExecTimeType = Union[list[TimeTypes], TimeTypes]
TIME_TYPES_STR = (
    "Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time]"
)

# execution time stamp typing for a oneshot Job
ExecOnceTimeType = Union[dt.datetime, TimeTypes]


class JobExecTimer:
    """
    Auxiliary timer class for the `Job` class.

    This timer is needed to parallelise the individual
    desired execution times and to treat them equally.

    Parameters
    ----------
    exec_at : Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time]
        Execution time.
    start_dt : datetime.datetime
        Reference `datetime.datetime` object. This reference is used to
        calculate the first execution and then recursively calculate all
        further executions.
    """

    def __init__(self, exec_at: TimeTypes, start_dt: dt.datetime):
        self.__exec_at = exec_at
        self.__exec_dt_stamp = start_dt

    def gen_next_exec_dt(self) -> None:
        """Generate the next execution `datetime.datetime` stamp."""
        # calculate datetime to next weekday at 00:00
        if isinstance(self.__exec_at, Weekday):
            self.__exec_dt_stamp = next_weekday_occurrence(
                self.__exec_dt_stamp, self.__exec_at
            )

        # calculate next available datetime for the given time
        elif isinstance(self.__exec_at, dt.time):
            self.__exec_dt_stamp = next_time_occurrence(
                self.__exec_dt_stamp, self.__exec_at
            )

        # calculate datetime to next weekday and add the given time
        elif isinstance(self.__exec_at, tuple):
            self.__exec_dt_stamp = next_weekday_time_occurrence(
                self.__exec_dt_stamp, *self.__exec_at
            )

        # just add the timedelta to the current datetime object
        else:  # isinstance(self.__exec_at, dt.timedelta):
            self.__exec_dt_stamp = self.__exec_dt_stamp + self.__exec_at

    @property
    def datetime(self) -> dt.datetime:
        """
        Get the `datetime.datetime` object for the planed execution.

        Returns
        -------
        datetime.datetime
            Execution `datetime.datetime` stamp.
        """
        return self.__exec_dt_stamp

    def timedelta(self, dt_stamp: dt.datetime) -> dt.timedelta:
        """
        Get the `timedelta` until the execution of this `Job`.

        Parameters
        ----------
        dt_stamp : datetime.datetime
            Time to be compared with the planned execution time
            to determine the time difference.

        Returns
        -------
        timedelta
            `timedelta` to the execution.
        """
        return self.__exec_dt_stamp - dt_stamp


class Job:
    r"""
    Implementation of a `Job` for the `Scheduler`.

    The `Job` represents a callback function and manages the
    metrics and time functionalities.

    Notes
    -----
    The user will not manually instantiate the `Job`,
    this can only be done via the `Scheduler`.
    However, after a `Job` has been created by the `Scheduler`,
    the user can access the reference to the `Job`
    and thus query the metrics.

    Parameters
    ----------
    handle : Callable[..., Any]
        Handle to a callback function.
    exec_at : Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time] | list[Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time]]
        Desired execution time(s).
    params : dict[str, Any]
        The payload arguments to pass to the function handle within a Job.
    weight : float
        Relative weight against other `Job`\ s.
    delay : bool
        If `False` the `Job` will executed instantly or at a given offset.
    offset : Optional[datetime.datetime]
        Set the reference `datetime.datetime` stamp the `Job` will be
        scheduled against. Default value is `datetime.datetime.now()`.
    max_attempts : int
        Number of times the `Job` will be executed. 0 <=> inf
    """

    def __init__(
        self,
        handle: Callable[..., Any],
        exec_at: ExecTimeType,
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        offset: Optional[dt.datetime] = None,
        tzinfo: Optional[dt.timezone] = None,
    ):

        self.__handle = handle
        self.__params = {} if params is None else params
        self.__max_attempts = max_attempts
        self.__weight = weight
        self.__delay = delay
        self.__tzinfo = tzinfo

        self.__attempts = 0

        try:
            tg.check_type("exec_at", exec_at, ExecTimeType)
        except TypeError as err:
            raise SchedulerError(
                "Wrong input! Select one of the following input types:\n"
                + f"{TIME_TYPES_STR} or \n"
                + f"list[{TIME_TYPES_STR}]"
            ) from err

        self.__start_dt = offset if offset else dt.datetime.now(self.__tzinfo)

        self.__timers: list[JobExecTimer]
        self.__pending_timer: JobExecTimer
        # exec_at: Union[Weekday, dt.time, dt.timedelta, tuple[Weekday, dt.time]]
        if not isinstance(exec_at, list):
            self.__timers = [JobExecTimer(exec_at, self.__start_dt)]
        # exec_at: list[Union[Weekday, dt.time, dt.timedelta, tuple[Weekday, dt.time]]]
        else:
            self.__timers = [JobExecTimer(ele, self.__start_dt) for ele in exec_at]

        # generate first dt_stamps for each JobExecTimer
        for timer in self.__timers:
            timer.gen_next_exec_dt()

        # calculate active JobExecTimer
        self.__set_pending_timer()

    def _exec(self) -> None:
        """Execute the callback function."""
        self.__handle(**self.__params)
        self.__attempts += 1

    def _repr(
        self,
    ) -> tuple[str, float, int, Union[float, int], float, str]:
        """Return the objects in __repr__ as a tuple."""
        dt_stamp = dt.datetime.now(self.__tzinfo)
        dt_timedelta = self.timedelta(dt_stamp)
        return (
            self.handle.__qualname__,
            self.__pending_timer.datetime,
            dt_timedelta,
            self.attemps,
            float("inf") if self.max_attemps == 0 else self.max_attemps,
            self.weight,
            dt_stamp.tzname(),
        )

    def __lt__(self, other: Job):
        dt_stamp = dt.datetime.now(self.__tzinfo)
        return (
            self.timedelta(dt_stamp).total_seconds()
            < other.timedelta(dt_stamp).total_seconds()
        )

    def __str__(self) -> str:
        repr = self._repr()
        return "{0}(...) {7} {8} {3}/{4} weight={5:.3f} tzinfo={6}".format(
            *repr, *[str(elem).split(".")[0] for elem in repr[1:3]]
        )

    def __repr__(self) -> str:
        repr = self._repr()
        return "<scheduler.Job: {0}, {7}, {8}, {3}/{4}, weight={5}, tzinfo={6}>".format(
            *repr, *[str(elem).split(".")[0] for elem in repr[1:3]]
        )

    @property
    def handle(self) -> Callable[..., Any]:
        """
        Get the callback function handle.

        Returns
        -------
        Callable
            Callback function.
        """
        return self.__handle

    def _gen_next_exec_dt(self) -> None:
        """Calculate the next estimated execution `datetime.datetime` of the `Job`."""
        self.__pending_timer.gen_next_exec_dt()
        self.__set_pending_timer()

    def __set_pending_timer(self) -> None:
        """Get the pending timer at the moment."""
        unsorted_timer_datetimes: dict[JobExecTimer, dt.datetime] = {}
        for timer in self.__timers:
            unsorted_timer_datetimes[timer] = timer.datetime

        sorted_timers = sorted(
            unsorted_timer_datetimes, key=unsorted_timer_datetimes.get
        )
        self.__pending_timer = sorted_timers[0]

    @property
    def _has_attempts_remaining(self) -> bool:
        """
        Check if a `Job` executed all its execution attempts.

        Returns
        -------
        bool
            True if the `Job` has no free execution attempts.
        """
        if self.__max_attempts == 0:
            return True
        return self.__attempts < self.__max_attempts

    @property
    def attemps(self) -> int:
        """
        Get the number of executions for a `Job`.

        Returns
        -------
        int
            Execution attemps.
        """
        return self.__attempts

    @property
    def max_attemps(self) -> int:
        """
        Get the execution limit for a `Job`.

        Returns
        -------
        int
            Max execution attemps.
        """
        return self.__max_attempts

    @property
    def weight(self) -> float:
        """
        Return the weight of the job instance.

        Returns
        -------
        float
            Job weight.
        """
        return self.__weight

    @property
    def datetime(self) -> dt.datetime:
        """
        Give the `datetime.datetime` object for the planed execution.

        Returns
        -------
        datetime.datetime
            Execution `datetime.datetime` stamp.
        """
        if not self.__delay and self.__attempts == 0:
            return self.__start_dt
        return self.__pending_timer.datetime

    def timedelta(self, dt_stamp: Optional[dt.datetime] = None) -> dt.timedelta:
        """
        Get the `timedelta` until the next execution of this `Job`.

        Parameters
        ----------
        dt_stamp : Optional[datetime.datetime]
            Time to be compared with the planned execution time
            to determine the time difference.

        Returns
        -------
        timedelta
            `timedelta` to the next execution.
        """
        if dt_stamp is None:
            dt_stamp = dt.datetime.now(self.__tzinfo)
        if not self.__delay and self.__attempts == 0:
            return self.__start_dt - dt_stamp
        return self.__pending_timer.timedelta(dt_stamp)
