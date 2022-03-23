"""
Implementation of a `asyncio` compatible in-process scheduler.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

from __future__ import annotations

import asyncio as aio
import datetime as dt
from typing import Any, Callable, Optional, Union, cast

import typeguard as tg

from scheduler.asyncio.job import Job
from scheduler.base.definition import JOB_TYPE_MAPPING, JobType
from scheduler.base.scheduler import BaseScheduler, select_jobs_by_tag
from scheduler.base.scheduler_util import str_cutoff
from scheduler.base.timingtype import (
    TimingCyclic,
    TimingDailyUnion,
    TimingJobUnion,
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


class Scheduler(BaseScheduler):
    r"""
    Implementation of an asyncio scheduler.

    This implementation enables the planning of |Job|\ s depending on time
    cycles, fixed times, weekdays, dates, weights, offsets and execution counts.

    Notes
    -----
    Due to the support of `datetime` objects, the |Scheduler| is able to work
    with timezones.

    Parameters
    ----------
    loop : asyncio.selector_events.BaseSelectorEventLoop
        Set a AsyncIO event loop, default is the global event loop
    tzinfo : datetime.tzinfo
        Set the timezone of the |Scheduler|.
    """

    def __init__(
        self,
        *,
        loop: Optional[aio.selector_events.BaseSelectorEventLoop] = None,
        tzinfo: Optional[dt.tzinfo] = None,
    ):
        self.__loop = loop if loop else aio.get_event_loop()
        self.__tzinfo = tzinfo
        self.__tz_str = dt.datetime.now(tzinfo).tzname()

        self.__jobs: dict[Job, aio.Task] = {}

    async def __supervise_job(self, job: Job) -> None:
        try:
            while job.has_attempts_remaining:
                sleep_seconds: float = job.timedelta().total_seconds()
                await aio.sleep(sleep_seconds)

                await job._exec()  # pylint: disable=protected-access

                reference_dt = dt.datetime.now(tz=self.__tzinfo)
                job._calc_next_exec(reference_dt)  # pylint: disable=protected-access

        except aio.CancelledError:  # TODO asyncio does not trigger this exception in pytest, why?
            pass  # pragma: no cover

        else:
            self.delete_job(job)

    def __repr__(self) -> str:
        return "scheduler.asyncio.scheduler.Scheduler({0}, jobs={{{1}}})".format(
            ", ".join((repr(elem) for elem in (self.__tzinfo,))),
            ", ".join([repr(job) for job in sorted(self.jobs)]),
        )

    def __headings(self) -> list[str]:
        headings = [
            f"tzinfo={self.__tz_str}",
            f"#jobs={len(self.__jobs)}",
        ]
        return headings

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
                row[4],
                str_cutoff(row[5] or "", c_width[3], False),
                str_cutoff(row[7], c_width[4], True),
                str_cutoff(f"{row[8]}/{row[9]}", c_width[5], True),
            )
            job_table += fstring.format(*entries)

        return scheduler_headings + job_table

    def get_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> set[Job]:
        r"""
        Get a set of |Job|\ s from the |Scheduler| by tags.

        If no tags or an empty set of tags are given defaults to returning
        all |Job|\ s.

        Parameters
        ----------
        tags : set[str]
            Tags to filter scheduled |Job|\ s.
            If no tags are given all |Job|\ s are returned.
        any_tag : bool
            False: To match a |Job| all tags have to match.
            True: To match a |Job| at least one tag has to match.

        Returns
        -------
        set[Job]
            Currently scheduled |Job|\ s.
        """
        if tags is None or tags == {}:
            return self.jobs
        return select_jobs_by_tag(self.jobs, tags, any_tag)

    @property
    def jobs(self) -> set[Job]:
        r"""
        Get the set of all `Job`\ s.

        Returns
        -------
        set[Job]
            Currently scheduled |Job|\ s.
        """
        return set(self.__jobs.keys())

    def __schedule(
        self,
        job_type: JobType,
        timing: Union[TimingCyclic, TimingDailyUnion, TimingWeeklyUnion],
        handle: Callable[..., None],
        **kwargs,
    ) -> Job:
        """Encapsulate the `Job` and add the `Scheduler`'s timezone."""
        if not isinstance(timing, list):
            timing_list = cast(TimingJobUnion, [timing])
        else:
            timing_list = cast(TimingJobUnion, timing)

        job = Job(
            job_type=job_type,
            timing=timing_list,
            handle=handle,
            tzinfo=self.__tzinfo,
            **kwargs,
        )

        task = self.__loop.create_task(self.__supervise_job(job))
        self.__jobs[job] = task

        return job

    def delete_job(self, job: Job) -> None:
        """
        Delete a `Job` from the `Scheduler`.

        Parameters
        ----------
        job : Job
            |Job| instance to delete.

        Returns
        -------
        bool
            True if deleted
        """
        task: aio.Task = self.__jobs.pop(job)
        _: bool = task.cancel()  # has to be true, because pop should raise

    def delete_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> int:
        r"""
        Delete a set of |Job|\ s from the |Scheduler| by tags.

        If no tags or an empty set of tags are given defaults to the deletion
        of all |Job|\ s.

        Parameters
        ----------
        tags : Optional[set[str]]
            Set of tags to identify target |Job|\ s.
        any_tag : bool
            False: To delete a |Job| all tags have to match.
            True: To delete a |Job| at least one tag has to match.
        """
        all_jobs: set[Job] = set(self.__jobs.keys())
        jobs_to_delete: set[Job]

        if tags is None or tags == {}:
            jobs_to_delete = all_jobs
        else:
            jobs_to_delete = select_jobs_by_tag(all_jobs, tags, any_tag)

        for job in jobs_to_delete:
            self.delete_job(job)

        return len(jobs_to_delete)

    def cyclic(self, timing: TimingCyclic, handle: Callable[..., None], **kwargs) -> Job:
        try:
            tg.check_type("timing", timing, TimingCyclic)
        except TypeError as err:
            raise SchedulerError(CYCLIC_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.CYCLIC, timing=timing, handle=handle, **kwargs)

    def minutely(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs) -> Job:
        try:
            tg.check_type("timing", timing, TimingDailyUnion)
        except TypeError as err:
            raise SchedulerError(MINUTELY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.MINUTELY, timing=timing, handle=handle, **kwargs)

    def hourly(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs) -> Job:
        try:
            tg.check_type("timing", timing, TimingDailyUnion)
        except TypeError as err:
            raise SchedulerError(HOURLY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.HOURLY, timing=timing, handle=handle, **kwargs)

    def daily(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs) -> Job:
        try:
            tg.check_type("timing", timing, TimingDailyUnion)
        except TypeError as err:
            raise SchedulerError(DAILY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.DAILY, timing=timing, handle=handle, **kwargs)

    def weekly(self, timing: TimingWeeklyUnion, handle: Callable[..., None], **kwargs) -> Job:
        try:
            tg.check_type("timing", timing, TimingWeeklyUnion)
        except TypeError as err:
            raise SchedulerError(WEEKLY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.WEEKLY, timing=timing, handle=handle, **kwargs)

    def once(
        self,
        timing: TimingOnceUnion,
        handle: Callable[..., None],
        *,
        args: tuple[Any] = None,
        kwargs: Optional[dict[str, Any]] = None,
        tags: Optional[list[str]] = None,
    ) -> Job:
        try:
            tg.check_type("timing", timing, TimingOnceUnion)
        except TypeError as err:
            raise SchedulerError(ONCE_TYPE_ERROR_MSG) from err
        if isinstance(timing, dt.datetime):
            return self.__schedule(
                job_type=JobType.CYCLIC,
                timing=dt.timedelta(),
                handle=handle,
                args=args,
                kwargs=kwargs,
                max_attempts=1,
                tags=tags,
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
        )
