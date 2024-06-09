"""
Implementation of essential functions and components for a `BaseJob`.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

import datetime as dt
from typing import Optional, Union, cast

from scheduler.base.job import BaseJobType
from scheduler.base.timingtype import (
    TimingCyclic,
    TimingDailyUnion,
    TimingJobUnion,
    TimingWeeklyUnion,
)
from scheduler.error import SchedulerError


def str_cutoff(string: str, max_length: int, cut_tail: bool = False) -> str:
    """
    Abbreviate a string to a given length.

    The resulting string will carry an indicator if it's abbreviated,
    like ``stri#``.

    Parameters
    ----------
    string : str
        String which is to be cut.
    max_length : int
        Max resulting string length.
    cut_tail : bool
        ``False`` for string abbreviation from the front, else ``True``.

    Returns
    -------
    str
        Resulting string
    """
    if max_length < 1:
        raise ValueError("max_length < 1 not allowed")

    if len(string) > max_length:
        pos = max_length - 1
        return string[:pos] + "#" if cut_tail else "#" + string[-pos:]

    return string


def check_tzname(tzinfo: Optional[dt.tzinfo]) -> Optional[str]:
    """Composed of the datetime.datetime.tzname and the datetime._check_tzname methode."""
    if tzinfo is None:
        return None
    name: Optional[str] = tzinfo.tzname(None)
    if not isinstance(name, str):
        raise SchedulerError(f"tzinfo.tzname() must return None or string, not {type(name)}")
    return name


def create_job_instance(
    job_class: type[BaseJobType],
    timing: Union[TimingCyclic, TimingDailyUnion, TimingWeeklyUnion],
    **kwargs,
) -> BaseJobType:
    """Create a job instance from the given input parameters."""
    if not isinstance(timing, list):
        timing_list = cast(TimingJobUnion, [timing])
    else:
        timing_list = cast(TimingJobUnion, timing)

    return job_class(
        timing=timing_list,
        **kwargs,
    )
