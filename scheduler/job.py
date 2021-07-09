"""
Implementation of a `Job` as callback function represention.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
from __future__ import annotations

import datetime as dt
from enum import Enum, auto
from threading import RLock


from typing import Callable, Optional, Union, Any, cast

import typeguard as tg

from scheduler.util import (
    TZ_ERROR_MSG,
    AbstractJob,
    SchedulerError,
    Weekday,
    next_minutely_occurrence,
    next_hourly_occurrence,
    next_daily_occurrence,
    next_weekday_occurrence,
    next_weekday_time_occurrence,
    prettify_timedelta,
    are_times_unique,
    are_weekday_times_unique,
)

# execution interval
TimingTypeCyclic = dt.timedelta
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

DUPLICATE_EFFECTIVE_TIME = "Times that are effectively identical are not allowed."

CYCLIC_TYPE_ERROR_MSG = (
    "Wrong input for Cyclic! Expected input type:\n" + "datetime.timedelta"
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


_TZ_ERROR_MSG = TZ_ERROR_MSG[:-1] + " for {0}."

START_STOP_ERROR = "Start argument must be smaller than the stop argument."


class JobType(Enum):  # in job
    """Indicate the `JobType` of a :class:`~scheduler.job.Job`."""

    CYCLIC = auto()
    MINUTELY = auto()
    HOURLY = auto()
    DAILY = auto()
    WEEKLY = auto()


JOB_TIMING_TYPE_MAPPING = {
    JobType.CYCLIC: {"type": TimingTypeCyclic, "err": CYCLIC_TYPE_ERROR_MSG},
    JobType.MINUTELY: {"type": TimingTypeDaily, "err": MINUTELY_TYPE_ERROR_MSG},
    JobType.HOURLY: {"type": TimingTypeDaily, "err": HOURLY_TYPE_ERROR_MSG},
    JobType.DAILY: {"type": TimingTypeDaily, "err": DAILY_TYPE_ERROR_MSG},
    JobType.WEEKLY: {"type": TimingTypeWeekly, "err": WEEKLY_TYPE_ERROR_MSG},
}

JOB_NEXT_DAYLIKE_MAPPING = {
    JobType.MINUTELY: next_minutely_occurrence,
    JobType.HOURLY: next_hourly_occurrence,
    JobType.DAILY: next_daily_occurrence,
}


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
        If ``True`` a :class:`~scheduler.job.Job` will only schedule it's newest planned
        execution and drop older ones.
    """

    def __init__(
        self,
        job_type: JobType,
        timing: TimingJobTimerUnion,
        start: dt.datetime,
        skip_missing: bool = False,
    ):
        self.__lock = RLock()
        self.__job_type = job_type
        self.__timing = timing
        self.__next_exec = start
        self.__skip = skip_missing

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
                #  check for _TimingTypeDay = Union[Weekday, tuple[Weekday, dt.time]]
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
    except TypeError as err:
        raise SchedulerError(JOB_TIMING_TYPE_MAPPING[job_type]["err"]) from err


class Job(AbstractJob):
    r"""
    `Job` class bundling time and callback function methods.

    Parameters
    ----------
    job_type : JobType
        Indicator which defines which calculations has to be used.
    timing : TimingTypeWeekly
        Desired execution time(s).
    handle : Callable[..., None]
        Handle to a callback function.
    params : dict[str, Any]
        The payload arguments to pass to the function handle within a
        :class:`~scheduler.job.Job`.
    weight : float
        Relative `weight` against other :class:`~scheduler.job.Job`\ s.
    delay : bool
        If ``False`` the :class:`~scheduler.job.Job` will executed instantly or at
        a given offset.
    start : Optional[datetime.datetime]
        Set the reference `datetime.datetime` stamp the :class:`~scheduler.job.Job`
        will be scheduled against. Default value is `datetime.datetime.now()`.
    stop : Optional[datetime.datetime]
        Define a point in time after which a :class:`~scheduler.job.Job` will be stopped
        and deleted.
    max_attempts : int
        Number of times the :class:`~scheduler.job.Job` will be executed where ``0 <=> inf``.
        A :class:`~scheduler.job.Job` with no free attempt will be deleted.
    skip_missing : bool
        If ``True`` a :class:`~scheduler.job.Job` will only schedule it's newest planned
        execution and drop older ones.
    tzinfo : datetime.timezone
        Set the timezone of the :class:`~scheduler.core.Scheduler` the :class:`~scheduler.job.Job`
        is scheduled in.

    Returns
    -------
    Job
        Instance of a scheduled :class:`~scheduler.job.Job`.
    """

    def __init__(
        self,
        job_type: JobType,
        timing: TimingJobUnion,
        handle: Callable[..., None],
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
        tzinfo: Optional[dt.timezone] = None,
    ):
        self.__lock = RLock()
        sane_timing_types(job_type, timing)
        self.__type = job_type
        self.__timing = timing
        self.__handle = handle
        self.__params = params or {}
        self.__max_attempts = max_attempts
        self.__weight = weight
        self.__delay = delay
        self.__start = start
        self.__stop = stop
        self.__skip_missing = skip_missing
        self.__tzinfo = tzinfo

        # self.__mark_delete will be set to True if the new Timer would be in future
        # relativ to the self.__stop variable
        self.__mark_delete = False
        self.__attempts = 0
        self.__timers: list[JobTimer]
        self.__pending_timer: JobTimer

        expanded_timing = self.__standardize_timing_format()
        self.__check_allowed_timezone_info(expanded_timing)
        self.__check_duplicate_effective_timings(expanded_timing)

        # create JobTimers
        self.__init_job_timers()

        if self.__stop is not None:
            if self.__pending_timer.datetime > self.__stop:
                self.__mark_delete = True

    def __standardize_timing_format(self) -> Optional[list[tuple[Weekday, dt.time]]]:
        if isinstance(self.__timing, list):
            if self.__type is JobType.MINUTELY:
                self.__timing = [
                    time.replace(hour=0, minute=0)
                    for time in cast(list[dt.time], self.__timing)
                ]
            elif self.__type is JobType.HOURLY:
                self.__timing = [
                    time.replace(hour=0) for time in cast(list[dt.time], self.__timing)
                ]
            elif self.__type is JobType.WEEKLY:
                return [
                    ele
                    if isinstance(ele, tuple)
                    else (ele, dt.time(tzinfo=self.__tzinfo))
                    for ele in cast(list[_TimingTypeDay], self.__timing)
                ]
        else:
            if self.__type is JobType.MINUTELY:
                self.__timing = cast(dt.time, self.__timing).replace(hour=0, minute=0)
            elif self.__type is JobType.HOURLY:
                self.__timing = cast(dt.time, self.__timing).replace(hour=0)
        return None

    def __check_allowed_timezone_info(
        self, expanded_timing: Optional[list[tuple[Weekday, dt.time]]]
    ):
        if isinstance(self.__timing, list):
            if self.__type is JobType.WEEKLY:
                for _, time in cast(list[tuple[Weekday, dt.time]], expanded_timing):
                    if bool(time.tzinfo) ^ bool(self.__tzinfo):
                        raise SchedulerError(TZ_ERROR_MSG)
            elif self.__type in (JobType.MINUTELY, JobType.HOURLY, JobType.DAILY):
                for time in cast(list[dt.time], self.__timing):
                    if bool(time.tzinfo) ^ bool(self.__tzinfo):
                        raise SchedulerError(TZ_ERROR_MSG)
        else:
            if self.__type is JobType.WEEKLY and isinstance(self.__timing, tuple):
                if bool(self.__timing[1].tzinfo) ^ bool(self.__tzinfo):
                    raise SchedulerError(TZ_ERROR_MSG)
            elif self.__type in (JobType.MINUTELY, JobType.HOURLY, JobType.DAILY):
                if bool(cast(dt.time, self.__timing).tzinfo) ^ bool(self.__tzinfo):
                    raise SchedulerError(TZ_ERROR_MSG)

        if self.__start:
            if bool(self.__start.tzinfo) ^ bool(self.__tzinfo):
                raise SchedulerError(_TZ_ERROR_MSG.format("start"))
        else:
            self.__start = dt.datetime.now(self.__tzinfo)

        if self.__stop:
            if bool(self.__stop.tzinfo) ^ bool(self.__tzinfo):
                raise SchedulerError(_TZ_ERROR_MSG.format("stop"))

        if self.__stop is not None:
            if self.__start >= self.__stop:
                raise SchedulerError(START_STOP_ERROR)

    def __check_duplicate_effective_timings(
        self, expanded_timing: Optional[list[tuple[Weekday, dt.time]]]
    ):
        if not isinstance(self.__timing, list):
            return
        if self.__type is JobType.WEEKLY:
            if not are_weekday_times_unique(
                cast(list[tuple[Weekday, dt.time]], expanded_timing), self.__tzinfo
            ):
                raise SchedulerError(DUPLICATE_EFFECTIVE_TIME)
        elif self.__type in (
            JobType.MINUTELY,
            JobType.HOURLY,
            JobType.DAILY,
        ):
            if not are_times_unique(cast(list[dt.time], self.__timing)):
                raise SchedulerError(DUPLICATE_EFFECTIVE_TIME)

    def __init_job_timers(self):
        if isinstance(self.__timing, list):
            self.__timers = [
                JobTimer(self.__type, tim, self.__start, self.__skip_missing)
                for tim in self.__timing
            ]
        else:
            self.__timers = [
                JobTimer(
                    self.__type,
                    cast(TimingJobTimerUnion, self.__timing),
                    self.__start,
                    self.__skip_missing,
                )
            ]

        # generate first dt_stamps for each JobTimer
        for timer in self.__timers:
            timer.calc_next_exec()

        # calculate active JobTimer
        self.__set_pending_timer()

    def _exec(self) -> None:
        """Execute the callback function."""
        with self.__lock:
            self.__handle(**self.__params)
            self.__attempts += 1

    def __lt__(self, other: Job):
        dt_stamp = dt.datetime.now(self.__tzinfo)
        return (
            self.timedelta(dt_stamp).total_seconds()
            < other.timedelta(dt_stamp).total_seconds()
        )

    def __repr__(self) -> str:
        with self.__lock:
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
        with self.__lock:
            dt_timedelta = self.timedelta(dt.datetime.now(self.__tzinfo))
            if hasattr(self.handle, "__code__"):
                f_args = "(..)" if self.handle.__code__.co_nlocals else "()"
            else:
                f_args = "(?)"
            return (
                self.__type.name if self.max_attempts != 1 else "ONCE",
                self.handle.__qualname__,
                f_args,
                self.datetime,
                str(self.datetime)[:19],
                self.datetime.tzname(),
                dt_timedelta,
                prettify_timedelta(dt_timedelta),
                self.attempts,
                float("inf") if self.max_attempts == 0 else self.max_attempts,
                self.weight,
            )

    def __str__(self) -> str:
        return "{0}, {1}{2}, at={4}, tz={5}, in={7}, #{8}/{9}, w={10:.3f}".format(
            *self._str()
        )

    @property
    def handle(self) -> Callable[..., None]:
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
            Reference time stamp to which the :class:`~scheduler.job.Job` calculates
            it's next execution.
        """
        with self.__lock:
            if self.__skip_missing:
                for timer in self.__timers:
                    if (timer.datetime - ref_dt).total_seconds() <= 0:
                        timer.calc_next_exec(ref_dt)
            else:
                self.__pending_timer.calc_next_exec(ref_dt)
            self.__set_pending_timer()
            if self.__stop is not None and self.__pending_timer.datetime > self.__stop:
                self.__mark_delete = True

    def __set_pending_timer(self) -> None:
        """Get the pending timer at the moment."""
        with self.__lock:
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

        This function will return True if the :class:`~scheduler.job.Job` has open
        execution counts and the stop argument is not in the past relative to the
        next planed execution.

        Returns
        -------
        bool
            True if the :class:`~scheduler.job.Job` has execution attempts.
        """
        with self.__lock:
            if self.__mark_delete:
                return False
            if self.__max_attempts == 0:
                return True
            return self.__attempts < self.__max_attempts

    @property
    def attempts(self) -> int:
        """
        Get the number of executions for a `Job`.

        Returns
        -------
        int
            Execution attempts.
        """
        return self.__attempts

    @property
    def max_attempts(self) -> int:
        """
        Get the execution limit for a `Job`.

        Returns
        -------
        int
            Max execution attempts.
        """
        return self.__max_attempts

    @property
    def type(self) -> JobType:
        """
        Return the `JobType` of the `Job` instance.

        Returns
        -------
        JobType
            :class:`~scheduler.job.JobType` of the :class:`~scheduler.job.Job`.
        """
        return self.__type

    @property
    def weight(self) -> float:
        """
        Return the weight of the `Job` instance.

        Returns
        -------
        float
            :class:`~scheduler.job.Job` `weight`.
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
        with self.__lock:
            if not self.__delay and self.__attempts == 0:
                return cast(dt.datetime, self.__start)
            return self.__pending_timer.datetime

    def timedelta(self, dt_stamp: Optional[dt.datetime] = None) -> dt.timedelta:
        """
        Get the `datetime.timedelta` until the next execution of this `Job`.

        Parameters
        ----------
        dt_stamp : Optional[datetime.datetime]
            Time to be compared with the planned execution time to determine the time difference.

        Returns
        -------
        timedelta
            `datetime.timedelta` to the next execution.
        """
        with self.__lock:
            if dt_stamp is None:
                dt_stamp = dt.datetime.now(self.__tzinfo)
            if not self.__delay and self.__attempts == 0:
                return cast(dt.datetime, self.__start) - dt_stamp
            return self.__pending_timer.timedelta(dt_stamp)

    @property
    def _tzinfo(self) -> Optional[dt.timezone]:
        """
        Get the timezone of the `Scheduler` in which the `Job` is living.

        Returns
        -------
        Optional[datetime.timezone]
            Timezone of the :class:`~scheduler.job.Job`.
        """
        return self.__tzinfo

    @property
    def tzinfo(self) -> Optional[dt.tzinfo]:
        r"""
        Get the timezone of the `Job`'s next execution.

        Returns
        -------
        Optional[datetime.timezone]
            Timezone of the :class:`~scheduler.job.Job`\ s next execution.
        """
        return self.datetime.tzinfo

    @property
    def start(self) -> Optional[dt.datetime]:
        """
        Get the timestamp at which the `JobTimer` starts.

        Returns
        -------
        Optional[datetime.datetime]
            The start datetime stamp.
        """
        return self.__start

    @property
    def stop(self) -> Optional[dt.datetime]:
        """
        Get the timestamp after which no more executions of the `Job` should be scheduled.

        Returns
        -------
        Optional[datetime.datetime]
            The stop datetime stamp.
        """
        return self.__stop
