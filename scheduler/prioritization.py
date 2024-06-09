"""
Collection of prioritization functions.

For compatibility with the |Scheduler|, the prioritization
functions have to be of type ``Callable[[float, Job, int, int], float]``.

Author: Jendrik A. Potyka, Fabian A. Preiss
"""

import random

from scheduler.base.job import BaseJobType
from scheduler.threading.job import Job


def constant_weight_prioritization(
    time_delta: float, job: Job, max_exec: int, job_count: int
) -> float:
    r"""
    Interprets the `Job`'s weight as its priority.

    Return the |Job|'s weight for overdue
    |Job|\ s, otherwise return zero:

    .. math::
        \left(\mathtt{time\_delta},\mathtt{weight}\right)\ {\mapsto}\begin{cases}
        0 & :\ \mathtt{time\_delta}<0\\
        \mathtt{weight} & :\ \mathtt{time\_delta}\geq0
        \end{cases}

    Parameters
    ----------
    time_delta : float
        The time in seconds that a |Job| is overdue.
    job : Job
        The |Job| instance
    max_exec : int
        Limits the number of overdue |Job|\ s that can be executed
        by calling function `Scheduler.exec_jobs()`.
    job_count : int
        Number of scheduled |Job|\ s

    Returns
    -------
    float
        The weight of a |Job| as priority.
    """
    _ = max_exec
    _ = job_count
    if time_delta < 0:
        return 0
    return job.weight


def linear_priority_function(time_delta: float, job: Job, max_exec: int, job_count: int) -> float:
    r"""
    Compute the |Job|\ s default linear priority.

    Linear |Job| prioritization such that the priority increases
    linearly with the amount of time that a |Job| is overdue.
    At the exact time of the scheduled execution, the priority is equal to the
    |Job|\ s weight.

    The function is defined as

    .. math::
        \left(\mathtt{time\_delta},\mathtt{weight}\right)\ {\mapsto}\begin{cases}
        0 & :\ \mathtt{time\_delta}<0\\
        {\left(\mathtt{time\_delta}+1\right)}\cdot\mathtt{weight} & :\ \mathtt{time\_delta}\geq0
        \end{cases}

    Parameters
    ----------
    time_delta : float
        The time in seconds that a |Job| is overdue.
    job : Job
        The |Job| instance
    max_exec : int
        Limits the number of overdue |Job|\ s that can be executed
        by calling function `Scheduler.exec_jobs()`.
    job_count : int
        Number of scheduled |Job|\ s

    Returns
    -------
    float
        The time dependant priority for a |Job|
    """
    _ = max_exec
    _ = job_count

    if time_delta < 0:
        return 0
    return (time_delta + 1) * job.weight


def random_priority_function(time: float, job: Job, max_exec: int, job_count: int) -> float:
    """
    Generate random priority values from weights.

    .. warning:: Not suitable for security relevant purposes.

    The priority generator will return 1 if the random number
    is lower then the |Job|'s weight, otherwise it will return 0.
    """
    _ = time
    _ = max_exec
    _ = job_count
    if random.random() < job.weight:  # nosec
        return 1
    return 0
