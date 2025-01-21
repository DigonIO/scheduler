"""
Implementation of a `threading` compatible in-process scheduler.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

import datetime as dt
import queue
import threading
from collections.abc import Iterable
from logging import Logger
from typing import Any, Callable, Optional

import typeguard as tg

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
    TZ_ERROR_MSG,
    WEEKLY_TYPE_ERROR_MSG,
)
from scheduler.prioritization import linear_priority_function
from scheduler.threading.job import Job


def _exec_job_worker(que: queue.Queue[Job], logger: Logger) -> None:
    running = True
    while running:
        try:
            job = que.get(block=False)
        except queue.Empty:
            running = False
        else:
            job._exec(logger=logger)  # pylint: disable=protected-access
            que.task_done()


class Scheduler(BaseScheduler[Job, Callable[..., None]]):
    r"""
    Implementation of a scheduler for callback functions.

    This implementation enables the planning of |Job|\ s depending on time
    cycles, fixed times, weekdays, dates, offsets, execution counts and weights.

    Notes
    -----
    Due to the support of `datetime` objects, `scheduler` is able to work
    with timezones.

    Parameters
    ----------
    tzinfo : datetime.tzinfo
        Set the timezone of the |Scheduler|.
    max_exec : int
        Limits the number of overdue |Job|\ s that can be executed
        by calling function `Scheduler.exec_jobs()`.
    priority_function : Callable[[float, Job, int, int], float]
        A function handle to compute the priority of a |Job| depending
        on the time it is overdue and its respective weight. Defaults to a linear
        priority function.
    jobs : set[Job]
        A collection of job instances.
    n_threads : int
        The number of worker threads. 0 for unlimited, default 1.
    logger : Optional[logging.Logger]
        A custom Logger instance.
    """

    def __init__(
        self,
        *,
        max_exec: int = 0,
        tzinfo: Optional[dt.tzinfo] = None,
        priority_function: Callable[
            [float, Job, int, int],
            float,
        ] = linear_priority_function,
        jobs: Optional[Iterable[Job]] = None,
        n_threads: int = 1,
        logger: Optional[Logger] = None,
    ):
        super().__init__(logger=logger)
        self.__max_exec = max_exec
        self.__tzinfo = tzinfo
        self.__priority_function = priority_function
        self.__jobs_lock = threading.RLock()
        if not jobs:
            self.__jobs = set()
        elif isinstance(jobs, set):
            self.__jobs = jobs
        else:
            self.__jobs = set(jobs)

        for job in self.__jobs:
            if job._tzinfo != self.__tzinfo:
                raise SchedulerError(TZ_ERROR_MSG)

        self.__n_threads = n_threads
        self.__tz_str = check_tzname(tzinfo=tzinfo)

    def __repr__(self) -> str:
        with self.__jobs_lock:
            return "scheduler.Scheduler({0}, jobs={{{1}}})".format(
                ", ".join(
                    (
                        repr(elem)
                        for elem in (
                            self.__max_exec,
                            self.__tzinfo,
                            self.__priority_function,
                        )
                    )
                ),
                ", ".join([repr(job) for job in sorted(self.jobs)]),
            )

    def __str__(self) -> str:
        with self.__jobs_lock:
            # Scheduler meta heading
            scheduler_headings = "{0}, {1}, {2}, {3}\n\n".format(*self.__headings())

            # Job table (we join two of the Job._repr() fields into one)
            # columns
            c_align = ("<", "<", "<", "<", ">", ">", ">")
            c_width = (8, 16, 19, 12, 9, 13, 6)
            c_name = (
                "type",
                "function / alias",
                "due at",
                "tzinfo",
                "due in",
                "attempts",
                "weight",
            )
            form = [
                f"{{{idx}:{align}{width}}}"
                for idx, (align, width) in enumerate(zip(c_align, c_width))
            ]
            if self.__tz_str is None:
                form = form[:3] + form[4:]

            fstring = " ".join(form) + "\n"
            job_table = fstring.format(*c_name) + fstring.format(
                *("-" * width for width in c_width)
            )
            for job in sorted(self.jobs):
                row = job._str()
                entries = (
                    row[0],
                    str_cutoff(row[1] + row[2], c_width[1], False),
                    row[3],
                    str_cutoff(row[4] or "", c_width[3], False),
                    str_cutoff(row[5], c_width[4], True),
                    str_cutoff(f"{row[6]}/{row[7]}", c_width[5], True),
                    str_cutoff(f"{job.weight}", c_width[6], True),
                )
                job_table += fstring.format(*entries)

            return scheduler_headings + job_table

    def __headings(self) -> list[str]:
        with self.__jobs_lock:
            headings = [
                f"max_exec={self.__max_exec if self.__max_exec else float('inf')}",
                f"tzinfo={self.__tz_str}",
                f"priority_function={self.__priority_function.__name__}",
                f"#jobs={len(self.__jobs)}",
            ]
            return headings

    def __schedule(
        self,
        **kwargs,
    ) -> Job:
        """Encapsulate the `Job` and add the `Scheduler`'s timezone."""
        job: Job = create_job_instance(Job, tzinfo=self.__tzinfo, **kwargs)
        if job.has_attempts_remaining:
            with self.__jobs_lock:
                self.__jobs.add(job)
        return job

    def __exec_jobs(self, jobs: list[Job], ref_dt: dt.datetime) -> int:
        n_jobs = len(jobs)

        que: queue.Queue[Job] = queue.Queue()
        for job in jobs:
            que.put(job)

        workers = []
        for _ in range(self.__n_threads or n_jobs):
            worker = threading.Thread(target=_exec_job_worker, args=(que, self._logger))
            worker.daemon = True
            worker.start()
            workers.append(worker)

        que.join()
        for worker in workers:
            worker.join()

        for job in jobs:
            job._calc_next_exec(ref_dt)  # pylint: disable=protected-access
            if not job.has_attempts_remaining:
                self.delete_job(job)

        return n_jobs

    def exec_jobs(self, force_exec_all: bool = False) -> int:
        r"""
        Execute scheduled `Job`\ s.

        By default executes the |Job|\ s that are overdue.

        |Job|\ s are executed in order of their priority
        :ref:`examples.weights`. If the |Scheduler| instance
        has a limit on the job execution counts per call of
        :func:`~scheduler.core.Scheduler.exec_jobs`, via the `max_exec` argument,
        |Job|\ s of lower priority might not get executed when
        competing |Job|\ s are overdue.

        Parameters
        ----------
        force_exec_all : bool
            Ignore the both - the status of the |Job| timers
            as well as the execution limit of the |Scheduler|

        Returns
        -------
        int
            Number of executed |Job|\ s.
        """
        ref_dt = dt.datetime.now(tz=self.__tzinfo)

        if force_exec_all:
            return self.__exec_jobs(list(self.__jobs), ref_dt)
        #  collect the current priority for all jobs

        job_priority: dict[Job, float] = {}
        n_jobs = len(self.__jobs)
        with self.__jobs_lock:
            for job in self.__jobs:
                delta_seconds = job.timedelta(ref_dt).total_seconds()
                job_priority[job] = self.__priority_function(
                    -delta_seconds,
                    job,
                    self.__max_exec,
                    n_jobs,
                )
        # sort the jobs by priority
        sorted_jobs = sorted(job_priority, key=job_priority.get, reverse=True)  # type: ignore
        # filter jobs by max_exec and priority greater zero
        filtered_jobs = [
            job
            for idx, job in enumerate(sorted_jobs)
            if (self.__max_exec == 0 or idx < self.__max_exec) and job_priority[job] > 0
        ]
        return self.__exec_jobs(filtered_jobs, ref_dt)

    def delete_job(self, job: Job) -> None:
        """
        Delete a `Job` from the `Scheduler`.

        Parameters
        ----------
        job : Job
            |Job| instance to delete.

        Raises
        ------
        SchedulerError
            Raises if the |Job| of the argument is not scheduled.
        """
        try:
            with self.__jobs_lock:
                self.__jobs.remove(job)
        except KeyError:
            raise SchedulerError("An unscheduled Job can not be deleted!") from None

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
            True: To deleta a |Job| at least one tag has to match.
        """
        with self.__jobs_lock:
            if tags is None or tags == set():
                n_jobs = len(self.__jobs)
                self.__jobs = set()
                return n_jobs

            to_delete = select_jobs_by_tag(self.__jobs, tags, any_tag)

            self.__jobs = self.__jobs - to_delete
            return len(to_delete)

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
        with self.__jobs_lock:
            if tags is None or tags == set():
                return self.__jobs.copy()
            return select_jobs_by_tag(self.__jobs, tags, any_tag)

    @deprecated(["delay"])
    def cyclic(self, timing: TimingCyclic, handle: Callable[..., None], **kwargs) -> Job:
        r"""
        Schedule a cyclic `Job`.

        Use a `datetime.timedelta` object or a `list` of `datetime.timedelta` objects
        to schedule a cyclic |Job|.

        Parameters
        ----------
        timing : TimingTypeCyclic
            Desired execution time.
        handle : Callable[..., None]
            Handle to a callback function.

        Returns
        -------
        Job
            Instance of a scheduled |Job|.

        Other Parameters
        ----------------
        **kwargs
            |Job| properties, optional

            `kwargs` are used to specify |Job| properties.

            Here is a list of available |Job| properties:

            .. include:: ../_assets/kwargs.rst
        """
        try:
            tg.check_type(timing, TimingCyclic)
        except tg.TypeCheckError as err:
            raise SchedulerError(CYCLIC_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.CYCLIC, timing=timing, handle=handle, **kwargs)

    @deprecated(["delay"])
    def minutely(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs) -> Job:
        r"""
        Schedule a minutely `Job`.

        Use a `datetime.time` object or a `list` of `datetime.time` objects
        to schedule a |Job| every minute.

        Notes
        -----
        If given a `datetime.time` object with a non zero hour or minute property, these
        information will be ignored.

        Parameters
        ----------
        timing : TimingDailyUnion
            Desired execution time(s).
        handle : Callable[..., None]
            Handle to a callback function.

        Returns
        -------
        Job
            Instance of a scheduled |Job|.

        Other Parameters
        ----------------
        **kwargs
            |Job| properties, optional

            `kwargs` are used to specify |Job| properties.

            Here is a list of available |Job| properties:

            .. include:: ../_assets/kwargs.rst
        """
        try:
            tg.check_type(timing, TimingDailyUnion)
        except tg.TypeCheckError as err:
            raise SchedulerError(MINUTELY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.MINUTELY, timing=timing, handle=handle, **kwargs)

    @deprecated(["delay"])
    def hourly(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs) -> Job:
        r"""
        Schedule an hourly `Job`.

        Use a `datetime.time` object or a `list` of `datetime.time` objects
        to schedule a |Job| every hour.

        Notes
        -----
        If given a `datetime.time` object with a non zero hour property, this information
        will be ignored.

        Parameters
        ----------
        timing : TimingDailyUnion
            Desired execution time(s).
        handle : Callable[..., None]
            Handle to a callback function.

        Returns
        -------
        Job
            Instance of a scheduled |Job|.

        Other Parameters
        ----------------
        **kwargs
            |Job| properties, optional

            `kwargs` are used to specify |Job| properties.

            Here is a list of available |Job| properties:

            .. include:: ../_assets/kwargs.rst
        """
        try:
            tg.check_type(timing, TimingDailyUnion)
        except tg.TypeCheckError as err:
            raise SchedulerError(HOURLY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.HOURLY, timing=timing, handle=handle, **kwargs)

    @deprecated(["delay"])
    def daily(self, timing: TimingDailyUnion, handle: Callable[..., None], **kwargs) -> Job:
        r"""
        Schedule a daily `Job`.

        Use a `datetime.time` object or a `list` of `datetime.time` objects
        to schedule a |Job| every day.

        Parameters
        ----------
        timing : TimingDailyUnion
            Desired execution time(s).
        handle : Callable[..., None]
            Handle to a callback function.

        Returns
        -------
        Job
            Instance of a scheduled |Job|.

        Other Parameters
        ----------------
        **kwargs
            |Job| properties, optional

            `kwargs` are used to specify |Job| properties.

            Here is a list of available |Job| properties:

            .. include:: ../_assets/kwargs.rst
        """
        try:
            tg.check_type(timing, TimingDailyUnion)
        except tg.TypeCheckError as err:
            raise SchedulerError(DAILY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.DAILY, timing=timing, handle=handle, **kwargs)

    @deprecated(["delay"])
    def weekly(self, timing: TimingWeeklyUnion, handle: Callable[..., None], **kwargs) -> Job:
        r"""
        Schedule a weekly `Job`.

        Use a `tuple` of a `Weekday` and a `datetime.time` object to define a weekly
        recurring |Job|. Combine multiple desired `tuples` in
        a `list`. If the planed execution time is `00:00` the `datetime.time` object
        can be ignored, just pass a `Weekday` without a `tuple`.

        Parameters
        ----------
        timing : TimingWeeklyUnion
            Desired execution time(s).
        handle : Callable[..., None]
            Handle to a callback function.

        Returns
        -------
        Job
            Instance of a scheduled |Job|.

        Other Parameters
        ----------------
        **kwargs
            |Job| properties, optional

            `kwargs` are used to specify |Job| properties.

            Here is a list of available |Job| properties:

            .. include:: ../_assets/kwargs.rst
        """
        try:
            tg.check_type(timing, TimingWeeklyUnion)
        except tg.TypeCheckError as err:
            raise SchedulerError(WEEKLY_TYPE_ERROR_MSG) from err
        return self.__schedule(job_type=JobType.WEEKLY, timing=timing, handle=handle, **kwargs)

    def once(  # pylint: disable=arguments-differ
        self,
        timing: TimingOnceUnion,
        handle: Callable[..., None],
        *,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        alias: Optional[str] = None,
        weight: float = 1,
    ) -> Job:
        r"""
        Schedule a oneshot `Job`.

        Parameters
        ----------
        timing : TimingOnceUnion
            Desired execution time.
        handle : Callable[..., None]
            Handle to a callback function.
        args : tuple[Any]
            Positional argument payload for the function handle within a |Job|.
        kwargs : Optional[dict[str, Any]]
            Keyword arguments payload for the function handle within a |Job|.
        tags : Optional[Iterable[str]]
            The tags of the |Job|.
        alias : Optional[str]
            Overwrites the function handle name in the string representation.
        weight : float
            Relative weight against other |Job|\ s.

        Returns
        -------
        Job
            Instance of a scheduled |Job|.
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
                weight=weight,
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
            weight=weight,
        )

    @property
    def jobs(self) -> set[Job]:
        r"""
        Get the set of all `Job`\ s.

        Returns
        -------
        set[Job]
            Currently scheduled |Job|\ s.
        """
        return self.__jobs.copy()
