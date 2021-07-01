"""
`Scheduler` implementation for `Job` based callback function execution.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
import datetime as dt

from typing import Callable, Optional, Any

import typeguard as tg

from scheduler.job import (
    TimingTypeCyclic,
    TimingTypeDaily,
    TimingTypeWeekly,
    TimingJobUnion,
    TimingTypeOnce,
    CYCLIC_TYPE_ERROR_MSG,
    MINUTELY_TYPE_ERROR_MSG,
    HOURLY_TYPE_ERROR_MSG,
    DAILY_TYPE_ERROR_MSG,
    WEEKLY_TYPE_ERROR_MSG,
    TZ_ERROR_MSG,
    JobType,
    Job,
)
from scheduler.util import (
    SchedulerError,
    AbstractJob,
    Weekday,
    linear_priority_function,
    str_cutoff,
)

ONCE_TYPE_ERROR_MSG = (
    "Wrong input for Once! Select one of the following input types:\n"
    + "dt.datetime | dt.timedelta | Weekday | dt.time | tuple[Weekday, dt.time]"
)


class Scheduler:  # in core
    r"""
    Implementation of a `Scheduler` for callback functions.

    This implementation enables the planning of :class:`~scheduler.job.Job`\ s depending on time
    cycles, fixed times, weekdays, dates, weights, offsets and execution counts.

    Notes
    -----
    Due to the support of `datetime` objects, `scheduler` is able to work
    with time zones.

    Parameters
    ----------
    tzinfo : datetime.timezone
        Set the time zone of the `Scheduler`.
    max_exec : int
        Limits the number of overdue `Job`\ s that can be executed
        by calling function `Scheduler.exec_jobs()`.
    priority_function : Callable[[float, Job, int, int], float]
        A function handle to compute the priority of a `Job` depending
        on the time it is overdue and its respective weight. Defaults to a linear
        priority function.
    jobs : set[Job]
        A collection of job instances.
    """

    def __init__(
        self,
        max_exec: int = 0,
        tzinfo: Optional[dt.timezone] = None,
        priority_function: Callable[
            [float, AbstractJob, int, int],
            float,
        ] = linear_priority_function,
        jobs: Optional[set[Job]] = None,
    ):
        self.__max_exec = max_exec
        self.__tzinfo = tzinfo
        self.__priority_function = priority_function
        self.__jobs: set[Job] = jobs or set()
        for job in self.__jobs:
            if job._tzinfo != self.__tzinfo:
                raise SchedulerError(TZ_ERROR_MSG)

        self.__tz_str = dt.datetime.now(tzinfo).tzname()

    def __repr__(self) -> str:
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

    def __headings(self) -> list[str]:
        headings = [
            f"max_exec={self.__max_exec if self.__max_exec else float('inf')}",
            f"timezone={self.__tz_str}",
            f"priority_function={self.__priority_function.__qualname__}",
            f"#jobs={len(self.__jobs)}",
        ]
        return headings

    def __str__(self) -> str:
        # Scheduler meta heading
        scheduler_headings = "{0}, {1}, {2}, {3}\n\n".format(*self.__headings())

        # Job table (we join two of the Job._repr() fields into one)
        # columns
        c_align = ("<", "<", "<", "<", ">", ">", ">")
        c_width = (8, 16, 19, 12, 9, 13, 6)
        c_name = (
            "type",
            "function",
            "due at",
            "timezone",
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
                str_cutoff(f"{row[10]}", c_width[6], True),
            )
            job_table += fstring.format(*entries)

        return scheduler_headings + job_table

    def delete_job(self, job: Job) -> None:
        """
        Delete a `Job` from the `Scheduler`.

        Parameters
        ----------
        job : Job
            `Job` instance to delete.
        """
        self.__jobs.remove(job)

    def delete_all_jobs(self) -> None:
        r"""Delete all `Job`\ s from the `Scheduler`."""
        self.__jobs = set()

    def __exec_job(self, job: Job, ref_dt: dt.datetime) -> None:
        """
        Execute a `Job` and handle it's deletion or new scheduling.

        Parameters
        ----------
        job : Job
            Instance of a `Job` to execute.
        ref_dt : datetime:datetime
            Reference time when the `Job` will be executed.
        """
        job._exec()

        # has to be calucalted bevor checking the attemps
        # because the next planned execution has to be evaluated
        # to compare it against the stop argument
        job._calc_next_exec(ref_dt)

        if not job.has_attempts_remaining:
            self.delete_job(job)

    def exec_jobs(self, force_exec_all: bool = False) -> int:
        r"""
        Execute scheduled `Job`\ s.

        By default executes the `Job`\ s that are overdue.

        `Job`\ s are executed in order of their priority :ref:`examples.weights`.
        If the `Scheduler` instance has a limit on the job execution counts
        per call of :func:`~scheduler.core.Scheduler.exec_jobs`, via the `max_exec`
        argument, `Job`\ s of lower priority might not get executed when competing `Job`\ s
        are overdue.

        Parameters
        ----------
        force_exec_all : bool
            Ignore the both - the status of the `Job` timers as well as the execution limit
            of the `Scheduler`

        Returns
        -------
        int
            Number of executed `Job`\ s.
        """
        ref_dt = dt.datetime.now(tz=self.__tzinfo)

        if force_exec_all:
            n_jobs = len(self.__jobs)
            for job in self.jobs:
                self.__exec_job(job, ref_dt)
            return n_jobs

        # get all jobs with overtime in seconds and weight
        job_priority: dict[Job, float] = {}
        for job in self.__jobs:
            delta_seconds = job.timedelta(ref_dt).total_seconds()
            job_priority[job] = -self.__priority_function(
                -delta_seconds,
                job,
                self.__max_exec,
                len(self.__jobs),
            )
        # sort the overtime jobs depending their weight * overtime
        sorted_jobs = sorted(job_priority, key=job_priority.get)  # type: ignore

        # execute the sorted overtime jobs and delete the ones with no attemps left
        exec_job_count = 0
        for idx, job in enumerate(sorted_jobs):
            if (self.__max_exec == 0 or idx < self.__max_exec) and job_priority[
                job
            ] < 0:
                self.__exec_job(job, ref_dt)
                exec_job_count += 1
            else:
                break
        return exec_job_count

    @property
    def jobs(self) -> set[Job]:
        r"""
        Get the set of all `Job`\ s.

        Returns
        -------
        set[Job]
            Currently scheduled `Job`\ s.
        """
        return self.__jobs.copy()

    def __schedule(
        self,
        job_type: JobType,
        timing: TimingJobUnion,
        handle: Callable[..., Any],
        params: Optional[dict[str, Any]],
        max_attempts: int,
        weight: float,
        delay: bool,
        start: Optional[dt.datetime],
        stop: Optional[dt.datetime],
        skip_missing: bool,
    ) -> Job:
        """Encapsulate the `Job` and add the `Scheduler` timezone."""
        job = Job(
            job_type=job_type,
            timing=timing,
            handle=handle,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
            tzinfo=self.__tzinfo,
        )
        if job.has_attempts_remaining:
            self.__jobs.add(job)
        return job

    def cyclic(
        self,
        timing: TimingTypeCyclic,
        handle: Callable[..., Any],
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
    ):
        r"""
        Schedule a cyclic `Job`.

        Use a `datetime.timedelta` object or a `list` of `datetime.timedelta` objects
        to schedule a cyclic `Job`.

        Parameters
        ----------
        timing : TimingTypeCyclic
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
            If `True` a `Job` will only do it's newest planned execution and
            drop older ones.

        Returns
        -------
        Job
            Instance of a scheduled `Job`.
        """
        try:
            tg.check_type("timing", timing, TimingTypeCyclic)
        except TypeError as err:
            raise SchedulerError(CYCLIC_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.CYCLIC,
            timing=timing,
            handle=handle,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
        )

    def minutely(
        self,
        timing: TimingTypeDaily,
        handle: Callable[..., Any],
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
    ):
        r"""
        Schedule a minutely `Job`.

        Use a `datetime.time` object or a `list` of `datetime.time` objects
        to schedule a `Job` every minute.

        Notes
        -----
        If the given `datetime.time` object has entries with a greater magnitude
        than seconds, e.g. minutes, this entries will be ignored.

        Parameters
        ----------
        timing : TimingTypeDaily
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
            If `True` a `Job` will only do it's newest planned execution and
            drop older ones.

        Returns
        -------
        Job
            Instance of a scheduled `Job`.
        """
        try:
            tg.check_type("timing", timing, TimingTypeDaily)
        except TypeError as err:
            raise SchedulerError(MINUTELY_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.MINUTELY,
            timing=timing,
            handle=handle,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
        )

    def hourly(
        self,
        timing: TimingTypeDaily,
        handle: Callable[..., Any],
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
    ):
        r"""
        Schedule a hourly `Job`.

        Use a `datetime.time` object or a `list` of `datetime.time` objects
        to schedule a `Job` every hour.

        Notes
        -----
        If the given `datetime.time` object has entries of type hour,
        this entries will be ignored.

        Parameters
        ----------
        timing : TimingTypeDaily
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
            If `True` a `Job` will only do it's newest planned execution and
            drop older ones.

        Returns
        -------
        Job
            Instance of a scheduled `Job`.
        """
        try:
            tg.check_type("timing", timing, TimingTypeDaily)
        except TypeError as err:
            raise SchedulerError(HOURLY_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.HOURLY,
            timing=timing,
            handle=handle,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
        )

    def daily(
        self,
        timing: TimingTypeDaily,
        handle: Callable[..., Any],
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
    ):
        r"""
        Schedule a daily `Job`.

        Use a `datetime.time` object or a `list` of `datetime.time` objects
        to schedule a `Job` every day.

        Parameters
        ----------
        timing : TimingTypeDaily
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
            If `True` a `Job` will only do it's newest planned execution and
            drop older ones.

        Returns
        -------
        Job
            Instance of a scheduled `Job`.
        """
        try:
            tg.check_type("timing", timing, TimingTypeDaily)
        except TypeError as err:
            raise SchedulerError(DAILY_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.DAILY,
            timing=timing,
            handle=handle,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
        )

    def weekly(
        self,
        timing: TimingTypeWeekly,
        handle: Callable[..., Any],
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
    ):
        r"""
        Schedule a weekly `Job`.

        Use a `tuple` of a `Weekday` and a `datetime.time` object to define a weekly recuring
        `Job`. Combine multiple desired `tuples` in a `list`. If the planed execution time
        is `00:00` the `datetime.time` object can be ingored, just pass a `Weekday` without
        a `tuple`.

        Parameters
        ----------
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
            If `True` a `Job` will only do it's newest planned execution and
            drop older ones.

        Returns
        -------
        Job
            Instance of a scheduled `Job`.
        """
        try:
            tg.check_type("timing", timing, TimingTypeWeekly)
        except TypeError as err:
            raise SchedulerError(WEEKLY_TYPE_ERROR_MSG) from err
        return self.__schedule(
            job_type=JobType.WEEKLY,
            timing=timing,
            handle=handle,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            start=start,
            stop=stop,
            skip_missing=skip_missing,
        )

    def once(
        self,
        timing: TimingTypeOnce,
        handle: Callable[..., Any],
        params: Optional[dict[str, Any]] = None,
        weight: float = 1,
    ):
        r"""
        Schedule a oneshot `Job`.

        Notes
        -----
        Usefull if a specific `datetime.datetime` for the planed execution
        is known.

        Parameters
        ----------
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

        Returns
        -------
        Job
            Instance of a scheduled `Job`.
        """
        try:
            tg.check_type("timing", timing, TimingTypeOnce)
        except TypeError as err:
            raise SchedulerError(ONCE_TYPE_ERROR_MSG) from err
        if isinstance(timing, dt.datetime):
            job = self.__schedule(
                job_type=JobType.CYCLIC,
                timing=dt.timedelta(),
                handle=handle,
                params=params,
                max_attempts=1,
                weight=weight,
                delay=False,
                start=timing,
                stop=None,
                skip_missing=False,
            )
        else:
            mapping = {
                dt.timedelta: JobType.CYCLIC,
                Weekday: JobType.WEEKLY,
                tuple: JobType.WEEKLY,
                dt.time: JobType.DAILY,
            }
            for timing_type, job_type in mapping.items():
                if isinstance(timing, timing_type):
                    job = self.__schedule(
                        job_type=job_type,
                        timing=timing,  # type: ignore
                        handle=handle,
                        params=params,
                        max_attempts=1,
                        weight=weight,
                        delay=True,
                        start=None,
                        stop=None,
                        skip_missing=False,
                    )
        return job
