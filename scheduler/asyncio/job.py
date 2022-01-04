"""
Implementation of job for the `asyncio` scheduler.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

from __future__ import annotations

from scheduler.base.job import BaseJob


class AsyncJob(BaseJob):
    r"""
    |AsyncJob| class bundling time and callback function methods.

    Parameters
    ----------
    job_type : JobType
        Indicator which defines which calculations has to be used.
    timing : TimingWeekly
        Desired execution time(s).
    handle : Callable[..., None]
        Handle to a callback function.
    args : tuple[Any]
        Positional argument payload for the function handle within a |AsyncJob|.
    kwargs : Optional[dict[str, Any]]
        Keyword arguments payload for the function handle within a |AsyncJob|.
    tags : Optional[set[str]]
        The tags of the |AsyncJob|.
    delay : Optional[bool]
        If ``True`` wait with the execution for the next scheduled time.
    start : Optional[datetime.datetime]
        Set the reference `datetime.datetime` stamp the |AsyncJob|
        will be scheduled against. Default value is `datetime.datetime.now()`.
    stop : Optional[datetime.datetime]
        Define a point in time after which a |AsyncJob| will be stopped
        and deleted.
    max_attempts : Optional[int]
        Number of times the |AsyncJob| will be executed where ``0 <=> inf``.
        A |AsyncJob| with no free attempt will be deleted.
    skip_missing : Optional[bool]
        If ``True`` a |AsyncJob| will only schedule it's newest planned
        execution and drop older ones.
    alias : Optional[str]
        Overwrites the function handle name in the string representation.
    tzinfo : Optional[datetime.tzinfo]
        Set the timezone of the |Scheduler| the |AsyncJob|
        is scheduled in.

    Returns
    -------
    AsyncJob
        Instance of a scheduled |AsyncJob|.
    """

    # pylint: disable=no-member invalid-name

    async def _exec(self):
        coroutine = self._BaseJob__handle(*self._BaseJob__args, **self._BaseJob__kwargs)
        await coroutine
        self._BaseJob__attempts += 1

    # pylint: enable=no-member invalid-name

    def __repr__(self) -> str:
        params: tuple[str] = self._repr()
        return f"scheduler.asyncio.job.AsyncJob({', '.join(params)})"

    def __str__(self) -> str:
        return "{0}, {1}{2}, at={4}, tz={5}, in={7}, #{8}/{9}".format(*self._str())
