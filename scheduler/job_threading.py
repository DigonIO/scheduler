"""
Implementation of a `Job` as callback function represention.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
from __future__ import annotations

import datetime as dt
import threading
from typing import Any, Callable, Optional, Union, cast

import typeguard as tg


class Job(AbstractJob):
    r"""
    |Job| class bundling time and callback function methods.

    Parameters
    ----------
    job_type : JobType
        Indicator which defines which calculations has to be used.
    timing : TimingWeekly
        Desired execution time(s).
    handle : Callable[..., None]
        Handle to a callback function.
    args : tuple[Any]
        Positional argument payload for the function handle within a |Job|.
    kwargs : Optional[dict[str, Any]]
        Keyword arguments payload for the function handle within a |Job|.
    tags : Optional[set[str]]
        The tags of the |Job|.
    weight : Optional[float]
        Relative `weight` against other |Job|\ s.
    delay : Optional[bool]
        If ``True`` wait with the execution for the next scheduled time.
    start : Optional[datetime.datetime]
        Set the reference `datetime.datetime` stamp the |Job|
        will be scheduled against. Default value is `datetime.datetime.now()`.
    stop : Optional[datetime.datetime]
        Define a point in time after which a |Job| will be stopped
        and deleted.
    max_attempts : Optional[int]
        Number of times the |Job| will be executed where ``0 <=> inf``.
        A |Job| with no free attempt will be deleted.
    skip_missing : Optional[bool]
        If ``True`` a |Job| will only schedule it's newest planned
        execution and drop older ones.
    alias : Optional[str]
        Overwrites the function handle name in the string representation.
    tzinfo : Optional[datetime.tzinfo]
        Set the timezone of the |Scheduler| the |Job|
        is scheduled in.

    Returns
    -------
    Job
        Instance of a scheduled |Job|.
    """

    __type: JobType
    __timing: TimingJobUnion
    __handle: Callable[..., None]
    __args: tuple[Any, ...]
    __kwargs: dict[str, Any]
    __max_attempts: int
    __tags: set[str]
    __weight: float
    __delay: bool
    __start: Optional[dt.datetime]
    __stop: Optional[dt.datetime]
    __skip_missing: bool
    __alias: Optional[str]
    __tzinfo: Optional[dt.tzinfo]

    __lock: threading.RLock
    __mark_delete: bool
    __attempts: int
    __pending_timer: JobTimer
    __timers: list[JobTimer]

    def __init__(
        self,
        job_type: JobType,
        timing: TimingJobUnion,
        handle: Callable[..., None],
        *,
        args: Optional[tuple[Any]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        tags: Optional[set[str]] = None,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
        alias: str = None,
        tzinfo: Optional[dt.tzinfo] = None,
    ):
        timing = JobUtil.standardize_timing_format(job_type, timing)

        JobUtil.sane_timing_types(job_type, timing)
        JobUtil.check_duplicate_effective_timings(job_type, timing, tzinfo)
        JobUtil.check_timing_tzinfo(job_type, timing, tzinfo)

        self.__start = JobUtil.set_start_check_stop_tzinfo(start, stop, tzinfo)

        self.__type = job_type
        self.__timing = timing
        # NOTE: https://github.com/python/mypy/issues/708
        #       https://github.com/python/mypy/issues/2427
        self.__handle = handle  # type: ignore
        self.__args = () if args is None else args
        self.__kwargs = {} if kwargs is None else kwargs.copy()
        self.__max_attempts = max_attempts
        self.__tags = set() if tags is None else tags.copy()
        self.__weight = weight
        self.__delay = delay
        self.__stop = stop
        self.__skip_missing = skip_missing
        self.__alias = alias
        self.__tzinfo = tzinfo

        self.__lock = threading.RLock()

        # self.__mark_delete will be set to True if the new Timer would be in future
        # relativ to the self.__stop variable
        self.__mark_delete = False
        self.__attempts = 0

        # create JobTimers
        self.__timers = [
            JobTimer(job_type, tim, self.__start, skip_missing) for tim in timing
        ]
        self.__pending_timer = JobUtil.get_pending_timer(self.__timers)

        if self.__stop is not None:
            if self.__pending_timer.datetime > self.__stop:
                self.__mark_delete = True

    def _exec(self) -> None:
        """Execute the callback function."""
        with self.__lock:
            self.__handle(*self.__args, **self.__kwargs)
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
                            self.__args,
                            self.__kwargs,
                            self.__max_attempts,
                            self.__weight,
                            self.__delay,
                            self.__start,
                            self.__stop,
                            self.__skip_missing,
                            self.__alias,
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
            if self.__alias is not None:
                f_args = ""
            elif hasattr(self.handle, "__code__"):
                f_args = "(..)" if self.handle.__code__.co_nlocals else "()"
            else:
                f_args = "(?)"
            return (
                self.__type.name if self.max_attempts != 1 else "ONCE",
                self.handle.__qualname__ if self.__alias is None else self.__alias,
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

    def _calc_next_exec(self, ref_dt: dt.datetime) -> None:
        """
        Calculate the next estimated execution `datetime.datetime` of the `Job`.

        Parameters
        ----------
        ref_dt : datetime.datetime
            Reference time stamp to which the |Job| calculates
            it's next execution.
        """
        with self.__lock:
            if self.__skip_missing:
                for timer in self.__timers:
                    if (timer.datetime - ref_dt).total_seconds() <= 0:
                        timer.calc_next_exec(ref_dt)
            else:
                self.__pending_timer.calc_next_exec(ref_dt)
            self.__pending_timer = JobUtil.get_pending_timer(self.__timers)
            if self.__stop is not None and self.__pending_timer.datetime > self.__stop:
                self.__mark_delete = True

    @property
    def type(self) -> JobType:
        """
        Return the `JobType` of the `Job` instance.

        Returns
        -------
        JobType
            :class:`~scheduler.job.JobType` of the |Job|.
        """
        return self.__type

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

    @property
    def args(self) -> tuple[Any, ...]:
        r"""
        Get the positional arguments of the function handle within a `Job`.

        .. warning:: When running |Job|\ s in parallel threads,
            be sure to implement possible side effects of parameter accessing in a
            thread safe manner.

        Returns
        -------
        tuple[Any]
            The payload arguments to pass to the function handle within a
            |Job|.
        """
        return self.__args

    @property
    def kwargs(self) -> dict[str, Any]:
        r"""
        Get the keyword arguments of the function handle within a `Job`.

        .. warning:: When running |Job|\ s in parallel threads,
            be sure to implement possible side effects of parameter accessing in a
            thread safe manner.

        Returns
        -------
        dict[str, Any]
            The payload arguments to pass to the function handle within a
            |Job|.
        """
        return self.__kwargs

    @property
    def tags(self) -> set[str]:
        r"""
        Get the tags of a `Job`.

        Returns
        -------
        set[str]
            The tags of a |Job|.
        """
        return self.__tags.copy()

    @property
    def weight(self) -> float:
        """
        Return the weight of the `Job` instance.

        Returns
        -------
        float
            |Job| `weight`.
        """
        return self.__weight

    @property
    def delay(self) -> bool:
        """
        Return ``True`` if the first `Job` execution will wait for the next scheduled time.

        Returns
        -------
        bool
            If ``True`` wait with the execution for the next scheduled time. If ``False``
            the first execution will target the time of `Job.start`.
        """
        return self.__delay

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
    def skip_missing(self) -> bool:
        """
        Return ``True`` if `Job` will only schedule it's newest planned execution.

        Returns
        -------
        bool
            If ``True`` a |Job| will only schedule it's newest planned
            execution and drop older ones.
        """
        return self.__skip_missing

    @property
    def tzinfo(self) -> Optional[dt.tzinfo]:
        r"""
        Get the timezone of the `Job`'s next execution.

        Returns
        -------
        Optional[datetime.tzinfo]
            Timezone of the |Job|\ s next execution.
        """
        return self.datetime.tzinfo

    @property
    def _tzinfo(self) -> Optional[dt.tzinfo]:
        """
        Get the timezone of the `Scheduler` in which the `Job` is living.

        Returns
        -------
        Optional[datetime.tzinfo]
            Timezone of the |Job|.
        """
        return self.__tzinfo

    @property
    def has_attempts_remaining(self) -> bool:
        """
        Check if a `Job` has remaining attempts.

        This function will return True if the |Job| has open
        execution counts and the stop argument is not in the past relative to the
        next planed execution.

        Returns
        -------
        bool
            True if the |Job| has execution attempts.
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
