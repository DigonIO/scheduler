"""
Implementation of job for the `threading` scheduler.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

import datetime as dt
import threading
from logging import Logger
from typing import Any, Callable, Optional

from scheduler.base.definition import JobType
from scheduler.base.job import BaseJob
from scheduler.base.timingtype import TimingJobUnion


class Job(BaseJob[Callable[..., None]]):
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
    max_attempts : Optional[int]
        Number of times the |Job| will be executed where ``0 <=> inf``.
        A |Job| with no free attempt will be deleted.
    tags : Optional[set[str]]
        The tags of the |Job|.
    delay : Optional[bool]
        *Deprecated*: If ``True`` wait with the execution for the next scheduled time.
    start : Optional[datetime.datetime]
        Set the reference `datetime.datetime` stamp the |Job|
        will be scheduled against. Default value is `datetime.datetime.now()`.
    stop : Optional[datetime.datetime]
        Define a point in time after which a |Job| will be stopped
        and deleted.
    skip_missing : Optional[bool]
        If ``True`` a |Job| will only schedule it's newest planned
        execution and drop older ones.
    alias : Optional[str]
        Overwrites the function handle name in the string representation.
    tzinfo : Optional[datetime.tzinfo]
        Set the timezone of the |Scheduler| the |Job|
        is scheduled in.
    weight : Optional[float]
        Relative `weight` against other |Job|\ s.

    Returns
    -------
    Job
        Instance of a scheduled |Job|.
    """

    __weight: float
    __lock: threading.RLock

    def __init__(
        self,
        job_type: JobType,
        timing: TimingJobUnion,
        handle: Callable[..., None],
        *,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        tags: Optional[set[str]] = None,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
        alias: Optional[str] = None,
        tzinfo: Optional[dt.tzinfo] = None,
        weight: float = 1,
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

    # pylint: disable=no-member invalid-name

    def _exec(self, logger: Logger) -> None:
        """Execute the callback function."""
        with self.__lock:
            try:
                self._BaseJob__handle(*self._BaseJob__args, **self._BaseJob__kwargs)  # type: ignore
            except Exception:
                logger.exception("Unhandled exception in `%r`!", self)
                self._BaseJob__failed_attempts += 1  # type: ignore
            self._BaseJob__attempts += 1  # type: ignore

    # pylint: enable=no-member invalid-name

    def _calc_next_exec(self, ref_dt: dt.datetime) -> None:
        with self.__lock:
            super()._calc_next_exec(ref_dt)

    def __repr__(self) -> str:
        with self.__lock:
            params: tuple[str, ...] = self._repr()
            params_sum: str = ", ".join(params[:6] + (repr(self.__weight),) + params[6:])
            return f"scheduler.Job({params_sum})"

    def __str__(self) -> str:
        return f"{super().__str__()}, w={self.weight:.3g}"

    def timedelta(self, dt_stamp: Optional[dt.datetime] = None) -> dt.timedelta:
        with self.__lock:
            return super().timedelta(dt_stamp)

    @property
    def datetime(self) -> dt.datetime:
        with self.__lock:
            return super().datetime

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
    def has_attempts_remaining(self) -> bool:
        with self.__lock:
            return super().has_attempts_remaining
