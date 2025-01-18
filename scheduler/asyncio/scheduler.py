"""
Implementation of a `asyncio` compatible in-process scheduler.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

from __future__ import annotations

import asyncio as aio
import datetime as dt
from asyncio.selector_events import BaseSelectorEventLoop
from collections.abc import Iterable
from logging import Logger
from typing import Any, Callable, Coroutine, Optional

import typeguard as tg

from scheduler.asyncio.job import Job
from scheduler.base.definition import JOB_TYPE_MAPPING, JobType
from scheduler.base.scheduler import BaseScheduler, deprecated, select_jobs_by_tag
from scheduler.base.scheduler_util import check_tzname, create_job_instance, str_cutoff
from scheduler.base.timingtype import (
    TimingCyclic,
    TimingDailyUnion,
    TimingOnceUnion,
    TimingWeeklyUnion,
)
from scheduler.error import SchedulerError
from scheduler.message import (
    CYCLIC_TYPE_ERROR_MSG,
    DAILY_TYPE_ERROR_MSG,
    HOURLY_TYPE_ERROR_MSG,
    MINUTELY_TYPE_ERROR_MSG,
    ONCE_TYPE_ERROR_MSG,
    WEEKLY_TYPE_ERROR_MSG,
)


class Scheduler(BaseScheduler[Job, Callable[..., Coroutine[Any, Any, None]]]):
    r"""
    Implementation of an asyncio scheduler.

    This implementation enables the planning of |AioJob|\ s depending on time
    cycles, fixed times, weekdays, dates, offsets and execution counts.

    Notes
    -----
    Due to the support of `datetime` objects, the |AioScheduler| is able to work
    with timezones.

    Parameters
    ----------
    loop : asyncio.selector_events.BaseSelectorEventLoop
        Set a AsyncIO event loop, default is the global event loop
    tzinfo : datetime.tzinfo
        Set the timezone of the |AioScheduler|.
    logger : Optional[logging.Logger]
        A custom Logger instance.
    """

    def __init__(
        self,
        *,
        loop: Optional[BaseSelectorEventLoop] = None,
        tzinfo: Optional[dt.tzinfo] = None,
        logger: Optional[Logger] = None,
    ):
        super().__init__(logger=logger)
        try:
            self.__loop = loop if loop else aio.get_running_loop()
        except RuntimeError:
            raise SchedulerError("The asyncio Scheduler requires a running event loop.") from None
        self.__tzinfo = tzinfo
        self.__tz_str = check_tzname(tzinfo=tzinfo)

        self._jobs: dict[Job, aio.Task[None]] = {}

    def __repr__(self) -> str:
        return "scheduler.asyncio.scheduler.Scheduler({0}, jobs={{{1}}})".format(
            ", ".join((repr(elem) for elem in (self.__tzinfo,))),
            ", ".join([repr(job) for job in sorted(self.jobs)]),
        )

    def __str__(self) -> str:
        # Scheduler meta heading
        scheduler_headings = "{0}, {1}\n\n".format(*self.__headings())

        # Job table (we join two of the Job._repr() fields into one)
        # columns
        c_align = ("<", "<", "<", "<", ">", ">")
        c_width = (8, 16, 19, 12, 9, 13)
        c_name = (
            "type",
            "function / alias",
            "due at",
            "tzinfo",
            "due in",
            "attempts",
        )
        form = [
            f"{{{idx}:{align}{width}}}" for idx, (align, width) in enumerate(zip(c_align, c_width))
        ]
        if self.__tz_str is None:
            form = form[:3] + form[4:]

        fstring = " ".join(form) + "\n"
        job_table = fstring.format(*c_name)
        job_table += fstring.format(*("-" * width for width in c_width))
        for job in sorted(self.jobs):
            row = job._str()
            entries = (
                row[0],
                str_cutoff(row[1] + row[2], c_width[1], False),
                row[3],
                str_cutoff(row[4] or "", c_width[3], False),
                str_cutoff(row[5], c_width[4], True),
                str_cutoff(f"{row[6]}/{row[7]}", c_width[5], True),
            )
            job_table += fstring.format(*entries)

        return scheduler_headings + job_table

    def __headings(self) -> list[str]:
        headings = [
            f"tzinfo={self.__tz_str}",
            f"#jobs={len(self._jobs)}",
        ]
        return headings

    def __schedule(
        self,
        **kwargs,
    ) -> Job:
        """Encapsulate the `Job` and add the `Scheduler`'s timezone."""
        job: Job = create_job_instance(Job, tzinfo=self.__tzinfo, **kwargs)

        task = self.__loop.create_task(self.__supervise_job(job))
        self._jobs[job] = task

        return job

    async def __supervise_job(self, job: Job) -> None:
        try:
            reference_dt = dt.datetime.now(tz=self.__tzinfo)
            while job.has_attempts_remaining:
                sleep_seconds: float = job.timedelta(reference_dt).total_seconds()
                await aio.sleep(sleep_seconds)

                await job._exec(logger=self._logger)  # pylint: disable=protected-access

                reference_dt = dt.datetime.now(tz=self.__tzinfo)
                job._calc_next_exec(reference_dt)  # pylint: disable=protected-access
        except aio.CancelledError:  # TODO asyncio does not trigger this exception in pytest, why?
            # raised, when `task.cancel()` in `delete_job` was run
            pass  # pragma: no cover
        else:
            self.delete_job(job)

    def delete_job(self, job: Job) -> None:
        """
        Delete a `Job` from the `Scheduler`.

        Parameters
        ----------
        job : Job
            |AioJob| instance to delete.

        Raises
        ------
        SchedulerError
            Raises if the |AioJob| of the argument is not scheduled.
        """
        try:
            task: aio.Task[None] = self._jobs.pop(job)
            _: bool = task.cancel()
        except KeyError:
            raise SchedulerError("An unscheduled Job can not be deleted!") from None

    def delete_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> int:
        r"""
        Delete a set of |AioJob|\ s from the |AioScheduler| by tags.

        If no tags or an empty set of tags are given defaults to the deletion
        of all |AioJob|\ s.

        Parameters
        ----------
        tags : Optional[set[str]]
            Set of tags to identify target |AioJob|\ s.
        any_tag : bool
            False: To delete a |AioJob| all tags have to match.
            True: To delete a |AioJob| at least one tag has to match.
        """
        all_jobs: set[Job] = set(self._jobs.keys())
        jobs_to_delete: set[Job]

        if tags is None or tags == set():
            jobs_to_delete = all_jobs
        else:
            jobs_to_delete = select_jobs_by_tag(all_jobs, tags, any_tag)

        for job in jobs_to_delete:
            self.delete_job(job)

        return len(jobs_to_delete)

    def get_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> set[Job]:
        r"""
        Get a set of |AioJob|\ s from the |AioScheduler| by tags.

        If no tags or an empty set of tags are given defaults to returning
        all |AioJob|\ s.

        Parameters
        ----------
        tags : set[str]
            Tags to filter scheduled |AioJob|\ s.
            If no tags are given all |AioJob|\ s are returned.
        any_tag : bool
            False: To match a |AioJob| all tags have to match.
            True: To match a |AioJob| at least one tag has to match.

        Returns
        -------
        set[Job]
            Currently scheduled |AioJob|\ s.
        """
        if tags is None or tags == set():
            return self.jobs
        return select_jobs_by_tag(self.jobs, tags, any_tag)

    @deprecated(["delay"])
    def cyclic(
        self, timing: TimingCyclic, handle: Callable[..., Coroutine[Any, Any, None]], **kwargs
    ) -> Job:
        r"""
        Schedule a cyclic `Job`.

        Use a `datetime.timedelta` object or a `list` of `datetime.timedelta` objects
        to schedule a cyclic |AioJob|.

        Parameters
        ----------
        timing : TimingTypeCyclic
            Desired execution time.
        handle : Callable[..., Coroutine[Any, Any, None]]
            Handle to a callback function.

        Returns
        -------
        Job
            Instance of a scheduled |AioJob|.

        Other Parameters
        ----------------
        **kwargs
            |AioJob| properties, optional

            `kwargs` are used to specify |AioJob| properties.

            Here is a list of available |AioJob| properties:

            .. include:: ../_assets/aio_kwargs.rst
        """
        try:
            tg.check_type(timing, TimingCyclic)
        except tg.TypeCheckError as err:
            raise SchedulerError(CYCLIC_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.CYCLIC, timing=timing, handle=handle, **kwargs)

    @deprecated(["delay"])
    def minutely(
        self, timing: TimingDailyUnion, handle: Callable[..., Coroutine[Any, Any, None]], **kwargs
    ) -> Job:
        r"""
        Schedule a minutely `Job`.

        Use a `datetime.time` object or a `list` of `datetime.time` objects
        to schedule a |AioJob| every minute.

        Notes
        -----
        If given a `datetime.time` object with a non zero hour or minute property, these
        information will be ignored.

        Parameters
        ----------
        timing : TimingDailyUnion
            Desired execution time(s).
        handle : Callable[..., Coroutine[Any, Any, None]]
            Handle to a callback function.

        Returns
        -------
        Job
            Instance of a scheduled |AioJob|.

        Other Parameters
        ----------------
        **kwargs
            |AioJob| properties, optional

            `kwargs` are used to specify |AioJob| properties.

            Here is a list of available |AioJob| properties:

            .. include:: ../_assets/aio_kwargs.rst
        """
        try:
            tg.check_type(timing, TimingDailyUnion)
        except tg.TypeCheckError as err:
            raise SchedulerError(MINUTELY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.MINUTELY, timing=timing, handle=handle, **kwargs)

    @deprecated(["delay"])
    def hourly(
        self, timing: TimingDailyUnion, handle: Callable[..., Coroutine[Any, Any, None]], **kwargs
    ) -> Job:
        r"""
        Schedule an hourly `Job`.

        Use a `datetime.time` object or a `list` of `datetime.time` objects
        to schedule a |AioJob| every hour.

        Notes
        -----
        If given a `datetime.time` object with a non zero hour property, this information
        will be ignored.

        Parameters
        ----------
        timing : TimingDailyUnion
            Desired execution time(s).
        handle : Callable[..., Coroutine[Any, Any, None]]
            Handle to a callback function.

        Returns
        -------
        Job
            Instance of a scheduled |AioJob|.

        Other Parameters
        ----------------
        **kwargs
            |AioJob| properties, optional

            `kwargs` are used to specify |AioJob| properties.

            Here is a list of available |AioJob| properties:

            .. include:: ../_assets/aio_kwargs.rst
        """
        try:
            tg.check_type(timing, TimingDailyUnion)
        except tg.TypeCheckError as err:
            raise SchedulerError(HOURLY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.HOURLY, timing=timing, handle=handle, **kwargs)

    @deprecated(["delay"])
    def daily(
        self, timing: TimingDailyUnion, handle: Callable[..., Coroutine[Any, Any, None]], **kwargs
    ) -> Job:
        r"""
        Schedule a daily `Job`.

        Use a `datetime.time` object or a `list` of `datetime.time` objects
        to schedule a |AioJob| every day.

        Parameters
        ----------
        timing : TimingDailyUnion
            Desired execution time(s).
        handle : Callable[..., Coroutine[Any, Any, None]]
            Handle to a callback function.

        Returns
        -------
        Job
            Instance of a scheduled |AioJob|.

        Other Parameters
        ----------------
        **kwargs
            |AioJob| properties, optional

            `kwargs` are used to specify |AioJob| properties.

            Here is a list of available |AioJob| properties:

            .. include:: ../_assets/aio_kwargs.rst
        """
        try:
            tg.check_type(timing, TimingDailyUnion)
        except tg.TypeCheckError as err:
            raise SchedulerError(DAILY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.DAILY, timing=timing, handle=handle, **kwargs)

    @deprecated(["delay"])
    def weekly(
        self, timing: TimingWeeklyUnion, handle: Callable[..., Coroutine[Any, Any, None]], **kwargs
    ) -> Job:
        r"""
        Schedule a weekly `Job`.

        Use a `tuple` of a `Weekday` and a `datetime.time` object to define a weekly
        recurring |AioJob|. Combine multiple desired `tuples` in
        a `list`. If the planed execution time is `00:00` the `datetime.time` object
        can be ignored, just pass a `Weekday` without a `tuple`.

        Parameters
        ----------
        timing : TimingWeeklyUnion
            Desired execution time(s).
        handle : Callable[..., Coroutine[Any, Any, None]]
            Handle to a callback function.

        Returns
        -------
        Job
            Instance of a scheduled |AioJob|.

        Other Parameters
        ----------------
        **kwargs
            |AioJob| properties, optional

            `kwargs` are used to specify |AioJob| properties.

            Here is a list of available |AioJob| properties:

            .. include:: ../_assets/aio_kwargs.rst
        """
        try:
            tg.check_type(timing, TimingWeeklyUnion)
        except tg.TypeCheckError as err:
            raise SchedulerError(WEEKLY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.WEEKLY, timing=timing, handle=handle, **kwargs)

    def once(
        self,
        timing: TimingOnceUnion,
        handle: Callable[..., Coroutine[Any, Any, None]],
        *,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        alias: Optional[str] = None,
    ) -> Job:
        r"""
        Schedule a oneshot `Job`.

        Parameters
        ----------
        timing : TimingOnceUnion
            Desired execution time.
        handle : Callable[..., Coroutine[Any, Any, None]]
            Handle to a callback function.
        args : tuple[Any]
            Positional argument payload for the function handle within a |AioJob|.
        kwargs : Optional[dict[str, Any]]
            Keyword arguments payload for the function handle within a |AioJob|.
        tags : Optional[Iterable[str]]
            The tags of the |AioJob|.
        alias : Optional[str]
            Overwrites the function handle name in the string representation.

        Returns
        -------
        Job
            Instance of a scheduled |AioJob|.
        """
        try:
            tg.check_type(timing, TimingOnceUnion)
        except tg.TypeCheckError as err:
            raise SchedulerError(ONCE_TYPE_ERROR_MSG) from err
        if isinstance(timing, dt.datetime):
            return self.__schedule(
                job_type=JobType.CYCLIC,
                timing=dt.timedelta(),
                handle=handle,
                args=args,
                kwargs=kwargs,
                max_attempts=1,
                tags=set(tags) if tags else set(),
                alias=alias,
                delay=False,
                start=timing,
            )
        return self.__schedule(
            job_type=JOB_TYPE_MAPPING[type(timing)],
            timing=timing,
            handle=handle,
            args=args,
            kwargs=kwargs,
            max_attempts=1,
            tags=tags,
            alias=alias,
        )

    @property
    def jobs(self) -> set[Job]:
        r"""
        Get the set of all `Job`\ s.

        Returns
        -------
        set[Job]
            Currently scheduled |AioJob|\ s.
        """
        return set(self._jobs.keys())
