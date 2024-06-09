"""
Implementation of job for the `asyncio` scheduler.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

from __future__ import annotations

from logging import Logger
from typing import Any, Callable, Coroutine

from scheduler.base.job import BaseJob


class Job(BaseJob[Callable[..., Coroutine[Any, Any, None]]]):
    r"""
    |AioJob| class bundling time and callback function methods.

    Parameters
    ----------
    job_type : JobType
        Indicator which defines which calculations has to be used.
    timing : TimingWeekly
        Desired execution time(s).
    handle : Callable[..., None]
        Handle to a callback function.
    args : tuple[Any]
        Positional argument payload for the function handle within a |AioJob|.
    kwargs : Optional[dict[str, Any]]
        Keyword arguments payload for the function handle within a |AioJob|.
    max_attempts : Optional[int]
        Number of times the |AioJob| will be executed where ``0 <=> inf``.
        A |AioJob| with no free attempt will be deleted.
    tags : Optional[set[str]]
        The tags of the |AioJob|.
    delay : Optional[bool]
        *Deprecated*: If ``True`` wait with the execution for the next scheduled time.
    start : Optional[datetime.datetime]
        Set the reference `datetime.datetime` stamp the |AioJob|
        will be scheduled against. Default value is `datetime.datetime.now()`.
    stop : Optional[datetime.datetime]
        Define a point in time after which a |AioJob| will be stopped
        and deleted.
    skip_missing : Optional[bool]
        If ``True`` a |AioJob| will only schedule it's newest planned
        execution and drop older ones.
    alias : Optional[str]
        Overwrites the function handle name in the string representation.
    tzinfo : Optional[datetime.tzinfo]
        Set the timezone of the |AioScheduler| the |AioJob|
        is scheduled in.

    Returns
    -------
    Job
        Instance of a scheduled |AioJob|.
    """

    # pylint: disable=no-member invalid-name

    async def _exec(self, logger: Logger) -> None:
        coroutine = self._BaseJob__handle(*self._BaseJob__args, **self._BaseJob__kwargs)  # type: ignore
        try:
            await coroutine
        except Exception:
            logger.exception("Unhandled exception in `%r`!", self)
            self._BaseJob__failed_attempts += 1  # type: ignore
        self._BaseJob__attempts += 1  # type: ignore

    # pylint: enable=no-member invalid-name

    def __repr__(self) -> str:
        params: tuple[str, ...] = self._repr()
        return f"scheduler.asyncio.job.Job({', '.join(params)})"
