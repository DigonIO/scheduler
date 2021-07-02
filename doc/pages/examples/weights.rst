.. _examples.weights:

Job Prioritization
==================

:class:`~scheduler.job.Job`\ s can be prioritized using `weight`\ s.
Prioritization becomes particulary relevant with increasing :class:`~scheduler.job.Job`
execution times compared to the :class:`~scheduler.core.Scheduler`\ s cycle length.

The `weight` parameter is available for all scheduling functions of
:class:`~scheduler.core.Scheduler`:

:func:`~scheduler.core.Scheduler.once`,
:func:`~scheduler.core.Scheduler.cyclic`,
:func:`~scheduler.core.Scheduler.minutely`,
:func:`~scheduler.core.Scheduler.hourly`,
:func:`~scheduler.core.Scheduler.daily`,
:func:`~scheduler.core.Scheduler.weekly`

.. _examples.weights.default_behaviour:

Default behaviour
-----------------

By default, the :class:`~scheduler.core.Scheduler` will prioritize using a linear function
(:func:`~scheduler.util.linear_priority_function`) that depends on the
:class:`~scheduler.job.Job`\ s `weight` and time it is overdue.

If several :class:`~scheduler.job.Job`\ s are scheduled for the same point in time,
they will be executed in order of their weights, starting with the :class:`~scheduler.job.Job`
of the highest weight:

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> now = dt.datetime.now()
    >>> sch = Scheduler(max_exec=3)

    >>> for weight in (2, 3, 1, 4):
    ...     job = sch.once(now, print, weight=weight, params={"end": f"{weight = }\n"})

    >>> exec_count = sch.exec_jobs()
    weight = 4
    weight = 3
    weight = 2

    >>> print(sch)  # doctest:+SKIP
    max_exec=3, timezone=None, priority_function=linear_priority_function, #jobs=1
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    ONCE     print(?)         2021-06-21 03:24:23  -0:00:00           0/1      1

Note that in this example the :class:`~scheduler.job.Job` with the lowest weight was not
executed, as the execution count per call for the :class:`~scheduler.core.Scheduler`
has been set to ``3`` via the `max_exec` parameter.

If several :class:`~scheduler.job.Job`\ s of the same weight are overdue, the
:class:`~scheduler.job.Job`\ s are prioritized by their delay, starting with the
:class:`~scheduler.job.Job` of the highest delay.

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> now = dt.datetime.now()
    >>> sch = Scheduler(max_exec=3)

    >>> for delayed_by in (2, 3, 1, 4):
    ...     exec_time = now - dt.timedelta(seconds=delayed_by)
    ...     job = sch.once(exec_time, print, params={"end": f"{delayed_by = }s\n"})

    >>> exec_count = sch.exec_jobs()
    delayed_by = 4s
    delayed_by = 3s
    delayed_by = 2s

    >>> print(sch)  # doctest:+SKIP
    max_exec=3, timezone=None, priority_function=linear_priority_function, #jobs=1
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    ONCE     print(?)         2021-06-21 03:24:23  -0:00:00           0/1      1