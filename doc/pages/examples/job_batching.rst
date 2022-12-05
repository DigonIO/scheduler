Job Batching
============

It is possible to bundle a |Job| with more than one
|JobTimer|. Except for :py:func:`~scheduler.core.Scheduler.once`
and :func:`~scheduler.core.Scheduler.cyclic`, |Scheduler| supports
passing of the `timing` argument via a `list` for the `scheduling` functions

:py:func:`~scheduler.core.Scheduler.minutely`,
:py:func:`~scheduler.core.Scheduler.hourly`,
:py:func:`~scheduler.core.Scheduler.daily` and
:py:func:`~scheduler.core.Scheduler.weekly`.

.. warning:: When bundling multiple times in a single |Job|, they
    are required to be distinct within the given context. Note that mixing of timezones
    can lead to indistinguishable times. If indistinguishable times are used, a
    :py:exc:`~scheduler.util.SchedulerError` will be raised.

For :py:func:`~scheduler.core.Scheduler.daily` we can embed several timers in one |Job| as follows:

.. code-block:: pycon

    >>> import datetime as dt
    >>> import time

    >>> from scheduler import Scheduler

    >>> def foo():
    ...     print("foo")
    ...

    >>> schedule = Scheduler()

    >>> timings = [dt.time(hour=0), dt.time(hour=12), dt.time(hour=18)]
    >>> schedule.daily(timing=timings, handle=foo)  # doctest:+ELLIPSIS
    scheduler.Job(...DAILY..., [...time(0, 0), ...time(12, 0), ...time(18, 0)]...)

In consequence, this |Scheduler| instance only contains a single |Job| instance of the `DAILY` type:

.. code-block:: pycon

    >>> print(schedule)  # doctest:+SKIP
    max_exec=inf, tzinfo=None, priority_function=linear_priority_function, #jobs=1
    <BLANKLINE>
    type     function / alias due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    DAILY    foo()            2021-06-20 12:00:00   9:23:13         0/inf      1
    <BLANKLINE>

In the given example, the job will be scheduled three times a day. Note that each call to
:py:meth:`~scheduler.core.Scheduler.exec_jobs` will only call the function handle
of the |Job| once, even if several timers are overdue.
