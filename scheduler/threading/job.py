"""
Implementation of job for the `threading` scheduler.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

import datetime as dt
import threading
from typing import Any, Callable, Optional, Union, cast

import typeguard as tg

from scheduler.base.definition import JobType
from scheduler.base.job import BaseJob
from scheduler.base.job_util import JobTimer, prettify_timedelta
from scheduler.base.timingtype import TimingJobUnion


class Job(BaseJob):
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
        super().__init__(
            job_type,
            timing,
            handle,
            args=args,
            kwargs=kwargs,
            max_attempts=max_attempts,
            tags=tags,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
            alias=alias,
            tzinfo=tzinfo,
        )
        self.__lock = threading.RLock()
        self.__weight = weight

    def _exec(self) -> None:
        """Execute the callback function."""
        with self.__lock:
            self._BaseJob__handle(*self._BaseJob__args, **self._BaseJob__kwargs)
            self._BaseJob__attempts += 1

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

    def _calc_next_exec(self, ref_dt: dt.datetime) -> None:
        with self.__lock:
            super()._calc_next_exec(ref_dt)

    @property
    def has_attempts_remaining(self) -> bool:
        with self.__lock:
            return super().has_attempts_remaining

    @property
    def datetime(self) -> dt.datetime:
        with self.__lock:
            return super().datetime

    def timedelta(self, dt_stamp: Optional[dt.datetime] = None) -> dt.timedelta:
        with self.__lock:
            return super().timedelta(dt_stamp)
