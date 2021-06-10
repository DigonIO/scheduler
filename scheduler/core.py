"""
`Scheduler` implementation for `Job` based callback function execution.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""
from __future__ import annotations

import datetime as dt
from typing import Callable, Optional, Any
from operator import itemgetter

import typeguard as tg

from scheduler.job import ExecOnceTimeType, ExecTimeType, Job
from scheduler.util import SchedulerError, str_cutoff, linear_weight_function


class Scheduler:
    r"""
    Implementation of a `Scheduler` for callback functions.

    This implementation enables the planning of `Job`\ s depending on time
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
    weight_function: Callable[[float, Job, int, int], float]
        A function handle to compute the effective weight of a `Job` depending
        on the time it is overdue and its respective weight. Defaults to a linear
        weight function.
    """

    def __init__(
        self,
        max_exec: int = 0,
        tzinfo: Optional[dt.timezone] = None,
        weight_function: Callable[
            [float, Job, int, int],
            float,
        ] = linear_weight_function,
    ):
        self.__tzinfo = tzinfo
        self.__max_exec = max_exec
        self.__weight_function = weight_function
        self.__jobs: set[Job] = set()

        self.__tz_str = dt.datetime.now(tzinfo).timetz().tzname()

    def __headings(self) -> list[str]:
        headings = [
            f"max_exec={self.__max_exec if self.__max_exec else float('inf')}",
            f"zinfo={self.__tz_str}",
            f"#jobs={len(self.__jobs)}",
            f"weight_function={self.__weight_function.__qualname__}",
        ]
        return headings

    def __str__(self) -> str:
        # Scheduler meta heading
        headings = "{0}, {1}, {2}, {3}\n\n".format(*self.__headings())

        # Job table (we join two of the Job._repr() fields into one)
        n_fields = 6
        jheadings = ["function", "due at", "due in", "attempts", "weight", "tzinfo"]
        column_width = [16, 19, 9, 13, 6, 12]

        collection = [job._repr() for job in sorted(self.jobs)]

        str_collection = []
        for row in collection:
            inner = []
            for idx, ele in enumerate(row):
                width = column_width[idx] if idx < 4 else column_width[idx - 1]
                if idx == 0:
                    tmp_str = str_cutoff(f"{ele}", width, False)
                elif idx == 1:
                    tmp_str = str(ele).split(".")[0]
                elif idx == 2:
                    # ~6x faster than with regex
                    tmp_str = str_cutoff(
                        str(ele).split(",")[0].split(".")[0], width, True
                    )
                elif idx == 3:
                    tmp_str = str_cutoff(f"{ele}/{row[idx+1]}", width, False)
                elif idx == 4:
                    continue
                elif idx == 5:
                    tmp_str = str_cutoff(f"{ele}", width, True)
                elif idx == 6:
                    tmp_str = str_cutoff(f"{ele}", width, False)
                inner.append(tmp_str)
            str_collection.append(inner)

        # right align except first column
        form = []
        for idx, length in zip(range(n_fields), column_width):
            align = ""
            if idx == 0:
                align = "<"
            if idx == 1:
                align = "^"
            if idx > 1:
                align = ">"
            form.append(f"{{{idx}:{align}{length}}}")

        fstring = f"{form[0]} {form[1]} {form[2]} {form[3]} {form[4]} {form[5]}\n"

        job_table = fstring.format(*jheadings)
        job_table += " ".join(["-" * width for width in column_width]) + "\n"
        for line in str_collection:
            job_table += fstring.format(*line)

        return headings + job_table

    def __repr__(self):
        res = f"<scheduler.Scheduler: {', '.join(self.__headings())}"
        res += f", jobs={{{', '.join([job.__repr__() for job in sorted(self.jobs)])}}}>"
        return res

    def _add_job(self, job: Job) -> None:
        """
        Add a `Job` to the `Scheduler`.

        Parameters
        ----------
        job : Job
            `Job` instance that has to be added to the `Scheduler`.
        """
        self.__jobs.add(job)

    def delete_job(self, job: Job) -> None:
        """
        Delete a `Job` from the `Scheduler`.

        Parameters
        ----------
        job : Job
            `Job` instance to delete.
        """
        self.__jobs.remove(job)

    def delete_jobs(self) -> None:
        r"""
        Delete all `Job`\ s from the `Scheduler`.

        """
        self.__jobs = set()

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

    def __exec_job(self, job: Job) -> None:
        """
        Execute a `Job` and handle it's deletion or new scheduling.

        Parameters
        ----------
        job : Job
            Instance of a `Job` to execute.
        """
        job._exec()
        if not job._has_attempts_remaining:
            self.delete_job(job)
        else:
            job._gen_next_exec_dt()

    def exec_all_jobs(self) -> int:
        r"""
        Execute all scheduled `Job`\ s independent of the planned execution time.

        Returns
        -------
        int
            Number of executed `Job`\ s.
        """
        n_jobs = len(self.__jobs)
        for job in self.__jobs:
            self.__exec_job(job)
        return n_jobs

    def exec_jobs(self) -> int:
        r"""
        Check the `Job`\ s that are overdue and carry them out.

        The `Job`\ s are prioritized by calculating their effective weights dependant
        on the `Job`'s weight and the amount of time it is overdue.

        If there is a limit to the number of `Job`\ s that can be
        performed in one call, the effective weight is relevant.

        Returns
        -------
        int
            Number of executed `Job`\ s.
        """
        # get all jobs with overtime in seconds and weight
        dt_stamp = dt.datetime.now(tz=self.__tzinfo)

        effective_weight: dict[Job, float] = {}
        for job in self.__jobs:
            delta_seconds = job.timedelta(dt_stamp).total_seconds()
            effective_weight[job] = -self.__weight_function(
                seconds=-delta_seconds,
                job=job,
                max_exec=self.__max_exec,
                job_count=len(self.__jobs),
            )
        # sort the overtime jobs depending their weight * overtime
        sorted_jobs = sorted(effective_weight, key=effective_weight.get)

        # execute the sorted overtime jobs and delete the ones with no attemps left
        exec_job_count = 0
        for idx, job in enumerate(sorted_jobs):
            if (self.__max_exec == 0 or idx < self.__max_exec) and effective_weight[
                job
            ] < 0:
                self.__exec_job(job)
                exec_job_count += 1
            else:
                break
        return exec_job_count

    def schedule(
        self,
        handle: Callable[..., Any],
        exec_at: ExecTimeType,
        params: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        weight: float = 1,
        delay: bool = True,
        offset: Optional[dt.datetime] = None,
    ) -> Job:
        r"""
        Create a repeating `Job` that will be executed in a given cycle.

        Parameters
        ----------
        handle : Callable[..., Any]
            Handle to a callback function.
        exec_at : Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time] | list[Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time]]
            Desired execution time(s).
        params : dict[str, Any]
            The payload arguments to pass to the function handle within a Job.
        weight : float
            Relative weight against other `Job`\ s.
        delay : bool
            If `False` the `Job` will executed instantly or at a given offset.
        offset : Optional[datetime.datetime]
            Set the reference `datetime.datetime` stamp the `Job` will be
            scheduled against. Default value is `datetime.datetime.now()`.
        max_attempts : int
            Number of times the `Job` will be executed. 0 <=> inf

        Returns
        -------
        Job
            Reference to the created `Job`.
        """
        job = Job(
            handle=handle,
            exec_at=exec_at,
            params=params,
            max_attempts=max_attempts,
            weight=weight,
            delay=delay,
            offset=offset,
            tzinfo=self.__tzinfo,
        )
        self._add_job(job)
        return job

    def once(
        self,
        handle: Callable[..., Any],
        exec_at: ExecOnceTimeType,
        params: Optional[dict[str, Any]] = None,
        weight: float = 1,
    ) -> Job:
        r"""
        Create a `Job` that runs once at a specific timestamp.

        Parameters
        ----------
        handle : Callable[..., Any]
            Handle to a callback function.
        exec_at : datetime.datetime | Weekday | datetime.time | datetime.timedelta | tuple[Weekday, datetime.time]
            Execution time.
        params : dict[str, Any]
            The payload arguments to pass to the function handle within a Job.
        weight : float
            Relativ job weight against other `Job`\ s.

        Returns
        -------
        Job
            Reference to the created `Job`.
        """
        try:
            tg.check_type("exec_at", exec_at, ExecOnceTimeType)
        except TypeError as err:
            raise SchedulerError(
                'Wrong input for "once"! Select one of the following input types:\n'
                + "datetime.datetime | Weekday | datetime.time | datetime.timedelta | "
                + "tuple[Weekday, datetime.time]"
            ) from err

        # hack to support dt.datetime objects as exec time
        if isinstance(exec_at, dt.datetime):
            # not testable with simple monkey patching because
            # patching of dt.datetime will corrupt the if statement
            return self.schedule(
                handle=handle,
                exec_at=dt.timedelta(days=1),  # dummy
                params=params,
                max_attempts=1,
                weight=weight,
                delay=False,
                offset=exec_at,
            )
        return self.schedule(
            handle=handle,
            exec_at=exec_at,
            params=params,
            max_attempts=1,
            weight=weight,
            delay=True,
            offset=None,
        )
