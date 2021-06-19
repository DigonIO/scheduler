Weights
^^^^^^^

:class:`~scheduler.job.Job`\ s can be weighted among each other.
This becomes more relevant the longer the execution of a
:class:`~scheduler.job.Job` is compared to the cycle length of the :class:`~scheduler.core.Scheduler` is.
It may be that the :class:`~scheduler.job.Job`\ s to be executed take longer than one
cycle of the :class:`~scheduler.core.Scheduler`. In order to enable a constant frequency,
the maximum number of :class:`~scheduler.job.Job`\ s to be executed can be limited.
This is illustrated in the following example with the help of
oneshot :class:`~scheduler.job.Job`\ s, but is also possible with normal :class:`~scheduler.job.Job`\ s:

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> timing = dt.datetime.now() + dt.timedelta(seconds=1)

    >>> def print_weight(x):
    ...     print(f"Weight: {x}")

    >>> sch = Scheduler(max_exec=3)
    >>> for weight in (2, 3, 1, 4):
    ...     _ = sch.once(timing, print_weight, weight=weight, params={"x": weight})

If the :class:`~scheduler.job.Job`\ s are now executed, only 3 of 4 :class:`~scheduler.job.Job`\ s are processed.
Note that a :class:`~scheduler.job.Job` in the next cycle is now one execution behind,
this can increase permanently depending on the situation and
the :class:`~scheduler.job.Job` cannot finish all overdue executions.

    >>> time.sleep(1)
    >>> print(sch.exec_pending_jobs())
    Weight: 4
    Weight: 3
    Weight: 2
    3