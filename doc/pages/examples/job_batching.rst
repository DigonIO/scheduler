Job Batching
============

It is possible to bundle a :class:`~scheduler.job.Job` with more than one
:class:`~scheduler.job.JobTimer`. Except for :func:`~scheduler.core.Scheduler.once`
and :func:`~scheduler.core.Scheduler.cyclic`, :class:`~scheduler.core.Scheduler` supports
passing of the `timing` argument via a `list` for the `scheduling` functions:

:func:`~scheduler.core.Scheduler.minutely`,
:func:`~scheduler.core.Scheduler.hourly`,
:func:`~scheduler.core.Scheduler.daily`,
:func:`~scheduler.core.Scheduler.weekly`


For :func:`~scheduler.core.Scheduler.daily` we can embed several timers in one `Job` as follows:

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> def foo():
    ...     print("foo")

    >>> sch = Scheduler()

    >>> timings = [dt.time(hour=12), dt.time(hour=18), dt.time(hour=0)]
    >>> sch.daily(timing=timings, handle=foo)  # doctest:+ELLIPSIS
    scheduler.Job(...DAILY..., [...time(12, 0), ...time(18, 0), ...time(0, 0)]...)

In consequence, this `Scheduler` instance only contains a single `Job` instance of the `DAILY` type:

.. code-block:: pycon

    >>> print(sch)  # doctest:+SKIP
    max_exec=inf, timezone=None, weight_function=linear_priority_function, #jobs=1
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    DAILY    foo()            2021-06-20 12:00:00   9:23:13         0/inf      1
    <BLANKLINE>

In the given example, the job will be scheduled three times a day. Note that each call to
:meth:`~scheduler.core.Scheduler.exec_jobs` will only call the function handle
of the `Job` once, even if several timers are overdue.