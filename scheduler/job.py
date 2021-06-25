"""
Implementation of a `Job` as callback function represention.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
from __future__ import annotations

import datetime as dt
from enum import Enum, auto

from typing import Callable, Optional, Union, Any, cast

import typeguard as tg

from scheduler.util import (
    AbstractJob,
    SchedulerError,
    Weekday,
    next_minutely_occurrence,
    next_hourly_occurrence,
    next_daily_occurrence,
    next_weekday_occurrence,
    next_weekday_time_occurrence,
)

# execution interval
TimingTypeCyclic = Union[dt.timedelta, list[dt.timedelta]]
# time on the clock
TimingTypeDaily = Union[dt.time, list[dt.time]]

# day of the week or time on the clock
_TimingTypeDay = Union[Weekday, tuple[Weekday, dt.time]]
TimingTypeWeekly = Union[_TimingTypeDay, list[_TimingTypeDay]]

TimingJobTimerUnion = Union[dt.timedelta, dt.time, _TimingTypeDay]
TimingJobUnion = Union[TimingTypeCyclic, TimingTypeDaily, TimingTypeWeekly]

# specify point in time, distance to reference time, day of the week or time on the clock
TimingTypeOnce = Union[
    dt.datetime, dt.timedelta, Weekday, dt.time, tuple[Weekday, dt.time]
]


CYCLIC_TYPE_ERROR_MSG = (
    "Wrong input for Cyclic! Select one of the following input types:\n"
    + "datetime.timedelta | list[datetime.timedelta]"
)
_DAILY_TYPE_ERROR_MSG = (
    "Wrong input for {0}! Select one of the following input types:\n"
    + "datetime.time | list[datetime.time]"
)
MINUTELY_TYPE_ERROR_MSG = _DAILY_TYPE_ERROR_MSG.format("Minutely")
HOURLY_TYPE_ERROR_MSG = _DAILY_TYPE_ERROR_MSG.format("Hourly")
DAILY_TYPE_ERROR_MSG = _DAILY_TYPE_ERROR_MSG.format("Daily")
WEEKLY_TYPE_ERROR_MSG = (
    "Wrong input for Weekly! Select one of the following input types:\n"
    + "DAY | list[DAY]\n"
    + "where `DAY = Weekday | tuple[Weekday, dt.time]`"
)

_TZ_ERROR_MSG = "Can't use offset-naive and offset-aware datetimes together for {0}."
TZ_ERROR_MSG = _TZ_ERROR_MSG[:-9] + "."

START_STOP_ERROR = "Start argument must be smaller than the stop argument."


class JobType(Enum):  # in job
    """Indicate the `JobType` of a `Job`."""

    CYCLIC = auto()
    MINUTELY = auto()
    HOURLY = auto()
    DAILY = auto()
    WEEKLY = auto()


def check_tz_aware(exec_at: dt.time, exec_dt: dt.datetime) -> None:
    """
    Raise if both arguments have incompatible timezone informations.

    Parameters
    ----------
    exec_at : datetime.time
        A time object
    exec_dt : datetime.datetime
        A datetime object

    Raises
    ------
    SchedulerError
        If one argument has a timezone and the other doesn't
    """
    if bool(exec_at.tzinfo) ^ bool(exec_dt.tzinfo):
        raise SchedulerError(TZ_ERROR_MSG)


class JobTimer:  # in job
    """
    The class provides the internal `datetime.datetime` calculations for `Job`.

    Parameters
    ----------
    job_type : JobType
        Indicator which defines which calculations has to be used.
    timing : TimingJobTimerUnion
        Desired execution time(s).
    start : datetime.datetime
        Timestamp reference from which future executions will be calculated.
    skip_missing : bool
        If `True` a `Job` will only schedule it's newest planned execution and
        drop older ones.
    """

    def __init__(
        self,
        job_type: JobType,
        timing: TimingJobTimerUnion,
        start: dt.datetime,
        skip_missing: bool = False,
    ):
        self.__job_type = job_type
        self.__timing = timing
        self.__next_exec = start
        self.__skip = skip_missing
        self.__tz_sanity_check(self.__next_exec)

    def __tz_sanity_check(self, exec_time):
        if self.__job_type in (JobType.MINUTELY, JobType.HOURLY, JobType.DAILY):
            check_tz_aware(self.__timing, exec_time)
        elif self.__job_type == JobType.WEEKLY:
            if not isinstance(self.__timing, Weekday):
                check_tz_aware(self.__timing[1], exec_time)

    def calc_next_exec(self, ref: Optional[dt.datetime] = None) -> None:
        """
        Generate the next execution `datetime.datetime` stamp.

        Parameters
        ----------
        ref : Optional[datetime.datetime]
            Datetime reference for scheduling the next execution datetime.
        """
        if ref:
            self.__tz_sanity_check(ref)

        if self.__job_type == JobType.CYCLIC:
            self.__next_exec = self.__next_exec + cast(dt.timedelta, self.__timing)

        elif self.__job_type == JobType.MINUTELY:
            self.__timing = cast(dt.time, self.__timing)
            if self.__next_exec.tzinfo:
                self.__next_exec = self.__next_exec.astimezone(self.__timing.tzinfo)
            self.__next_exec = next_minutely_occurrence(self.__next_exec, self.__timing)

        elif self.__job_type == JobType.HOURLY:
            self.__timing = cast(dt.time, self.__timing)
            if self.__next_exec.tzinfo:
                self.__next_exec = self.__next_exec.astimezone(self.__timing.tzinfo)
            self.__next_exec = next_hourly_occurrence(self.__next_exec, self.__timing)

        elif self.__job_type == JobType.DAILY:
            self.__timing = cast(dt.time, self.__timing)
            if self.__next_exec.tzinfo:
                self.__next_exec = self.__next_exec.astimezone(self.__timing.tzinfo)
            self.__next_exec = next_daily_occurrence(self.__next_exec, self.__timing)

        elif self.__job_type == JobType.WEEKLY:
            # check for _TimingTypeDay = Union[Weekday, tuple[Weekday, dt.time]]
            if isinstance(self.__timing, Weekday):
                self.__next_exec = next_weekday_occurrence(
                    self.__next_exec, self.__timing
                )
            else:
                self.__timing = cast(tuple[Weekday, dt.time], self.__timing)
                if self.__timing[1].tzinfo:
                    self.__next_exec = self.__next_exec.astimezone(
                        self.__timing[1].tzinfo
                    )
                self.__next_exec = next_weekday_time_occurrence(
                    self.__next_exec, *self.__timing
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
        return self.__next_exec - dt_stamp


def sane_timing_types(job_type: JobType, timing: TimingJobUnion) -> None:
    """
    Determine if a given `timing` fulfill the `Type` for a specific `JobType`.

    Parameters
    ----------
    job_type : JobType
        `JobType` to test agains.
    timing : TimingJobUnion
        The `timing` object to be tested.

    Raises
    ------
    TypeError
        If the `timing` object has the wrong `Type` for a specific `JobType`.
    """
    mapping = {
        JobType.CYCLIC: {"type": TimingTypeCyclic, "err": CYCLIC_TYPE_ERROR_MSG},
        JobType.MINUTELY: {"type": TimingTypeDaily, "err": MINUTELY_TYPE_ERROR_MSG},
        JobType.HOURLY: {"type": TimingTypeDaily, "err": HOURLY_TYPE_ERROR_MSG},
        JobType.DAILY: {"type": TimingTypeDaily, "err": DAILY_TYPE_ERROR_MSG},
        JobType.WEEKLY: {"type": TimingTypeWeekly, "err": WEEKLY_TYPE_ERROR_MSG},
    }

    try:
        tg.check_type("timing", timing, mapping[job_type]["type"])
    except TypeError as err:
        raise SchedulerError(mapping[job_type]["err"]) from err


class Job(AbstractJob):  # in job
    r"""
    `Job` class bundling time and callback function methods.

    Parameters
    ----------
    job_type : JobType
        Indicator which defines which calculations has to be used.
    timing : TimingTypeWeekly
        Desired execution time(s).
    handle : Callable[..., Any]
        Handle to a callback function.
    params : dict[str, Any]
        The payload arguments to pass to the function handle within a Job.
    weight : float
        Relative weight against other `Job`\ s.
    delay : bool
        If `False` the `Job` will executed instantly or at a given offset.
    start : Optional[datetime.datetime]
        Set the reference `datetime.datetime` stamp the `Job` will be
        scheduled against. Default value is `datetime.datetime.now()`.
    end : Optional[datetime.datetime]
        Define a point in time after which a `Job` will be stopped and deleted.
    max_attempts : int
        Number of times the `Job` will be executed. 0 <=> inf
        A `Job` with no free attempt will be deleted.
    skip_missing : bool
        If `True` a `Job` will only schedule it's newest planned execution and
        drop older ones.
    tzinfo : datetime.timezone
        Set the timeW zone of the `Scheduler` the `Job` is scheduled in.

    Returns
    -------
    Job
        Instance of a scheduled `Job`.
    """

    def __init__(
        self,
        job_type: JobType,
        timing: TimingJobUnion,
        handle: Callable[..., Any],
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
        tzinfo: Optional[dt.timezone] = None,
    ):
        sane_timing_types(job_type, timing)
        self.__type = job_type
        self.__timing = timing
        self.__handle = handle
        self.__params = {} if params is None else params
        self.__max_attempts = max_attempts
        self.__weight = weight
        self.__delay = delay
        self.__start: dt.datetime
        self.__skip_missing = skip_missing
        self.__tzinfo = tzinfo

        # self.__mark_delete will be set to True if the new Timer would be in future
        # relativ to the self.__stop variable
        self.__stop: Optional[dt.datetime] = None
        self.__mark_delete = False

        self.__attempts = 0
        self.__timers: list[JobTimer]
        self.__pending_timer: JobTimer

        if start:
            if bool(start.tzinfo) ^ bool(self.__tzinfo):
                raise SchedulerError(_TZ_ERROR_MSG.format("start"))
            self.__start = start
        else:
            self.__start = dt.datetime.now(self.__tzinfo)

        if stop:
            if bool(stop.tzinfo) ^ bool(self.__tzinfo):
                raise SchedulerError(_TZ_ERROR_MSG.format("stop"))
            self.__stop = stop

        if start is not None and stop is not None:
            if start >= stop:
                raise SchedulerError(START_STOP_ERROR)

        if not isinstance(timing, list):
            self.__timers = [JobTimer(job_type, timing, self.__start, skip_missing)]
        else:
            self.__timers = [
                JobTimer(job_type, tim, self.__start, skip_missing) for tim in timing
            ]
        # generate first dt_stamps for each JobTimer
        for timer in self.__timers:
            timer.calc_next_exec()

        # calculate active JobTimer
        self.__set_pending_timer()

        if stop is not None:
            if self.__pending_timer.datetime > stop:
                self.__mark_delete = True

    def _exec(self) -> None:
        """Execute the callback function."""
        self.__handle(**self.__params)
        self.__attempts += 1

    def __lt__(self, other: Job):
        dt_stamp = dt.datetime.now(self.__tzinfo)
        return (
            self.timedelta(dt_stamp).total_seconds()
            < other.timedelta(dt_stamp).total_seconds()
        )

    def __repr__(self) -> str:
        return "scheduler.Job({})".format(
            ", ".join(
                (
                    repr(elem)
                    for elem in (
                        self.__type,
                        self.__timing,
                        self.__handle,
                        self.__params,
                        self.__max_attempts,
                        self.__weight,
                        self.__delay,
                        self.__start,
                        self.__stop,
                        self.__skip_missing,
                        self.tzinfo,
                    )
                )
            )
        )

    def _str(
        self,
    ) -> tuple[
        str,
        str,
        str,
        dt.datetime,
        str,
        Optional[str],
        dt.timedelta,
        str,
        int,
        Union[float, int],
        float,
    ]:
        """Return the objects relevant for readable string representation."""
        dt_timedelta = self.timedelta(dt.datetime.now(self.__tzinfo))
        if hasattr(self.handle, "__code__"):
            f_args = "(..)" if self.handle.__code__.co_nlocals else "()"
        else:
            f_args = "(?)"
        return (
            self.__type.name if self.max_attemps != 1 else "ONCE",
            self.handle.__qualname__,
            f_args,
            self.datetime,
            str(self.datetime)[:19],
            self.datetime.tzname(),
            dt_timedelta,
            str(dt_timedelta)
            .split(",")[0]
            .split(".")[0],  # TODO fix representation, rounding is misleading
            self.attemps,
            float("inf") if self.max_attemps == 0 else self.max_attemps,
            self.weight,
        )

    def __str__(self) -> str:
        return "{0}, {1}{2}, at={4}, tz={5}, in={7}, #{8}/{9}, w={10:.3f}".format(
            *self._str()
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

    def _calc_next_exec(self, ref_dt: dt.datetime) -> None:
        """
        Calculate the next estimated execution `datetime.datetime` of the `Job`.

        Parameters
        ----------
        ref_dt : datetime.datetime
            Reference time stamp to which the `Job` caluclates it's next execution.
        """
        self.__pending_timer.calc_next_exec(ref_dt)
        self.__set_pending_timer()
        if self.__stop is not None:
            if self.__pending_timer.datetime > self.__stop:
                self.__mark_delete = True

    def __set_pending_timer(self) -> None:
        """Get the pending timer at the moment."""
        unsorted_timer_datetimes: dict[JobTimer, dt.datetime] = {}
        for timer in self.__timers:
            unsorted_timer_datetimes[timer] = timer.datetime

        sorted_timers = sorted(
            unsorted_timer_datetimes,
            key=unsorted_timer_datetimes.get,  # type: ignore
        )
        self.__pending_timer = sorted_timers[0]

    @property
    def has_attempts_remaining(self) -> bool:
        """
        Check if a `Job` has remaining attempts.

        This function will return True if the `Job` has open
        execution counts and the stop argument is not in
        the past relative to the next planed execution.

        Returns
        -------
        bool
            True if the `Job` has execution attempts.
        """
        if self.__mark_delete:
            return False
        elif self.__max_attempts == 0:
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
    def type(self) -> JobType:
        """
        Return the `JobType` of the `Job` instance.

        Returns
        -------
        JobType
            `JobType` of the `Job`.
        """
        return self.__type

    @property
    def weight(self) -> float:
        """
        Return the weight of the `Job` instance.

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
            return self.__start
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
            return self.__start - dt_stamp
        return self.__pending_timer.timedelta(dt_stamp)

    @property
    def _tzinfo(self) -> Optional[dt.timezone]:
        """
        Get the timezone of the `Scheduler` in which the `Job` is living.

        Returns
        -------
        Optional[datetime.timezone]
            Timezone of the `Job`.
        """
        return self.__tzinfo

    @property
    def tzinfo(self) -> Optional[dt.tzinfo]:
        r"""
        Get the timezone of the `Job`\ s next execution.

        Returns
        -------
        Optinal[datetime.timezone]
            Timezone of the `Job`\ s next execution.
        """
        return self.datetime.tzinfo
