.. _examples.weights:

Job Prioritization
==================

|Job|\ s can be prioritized using `weight`\ s.
Prioritization becomes particulary relevant with increasing |Job|
execution times compared to the |Scheduler|\ s cycle length.

The `weight` parameter is available for all scheduling functions of
|Scheduler|:

:py:func:`~scheduler.core.Scheduler.once`,
:py:func:`~scheduler.core.Scheduler.cyclic`,
:py:func:`~scheduler.core.Scheduler.minutely`,
:py:func:`~scheduler.core.Scheduler.hourly`,
:py:func:`~scheduler.core.Scheduler.daily`,
:py:func:`~scheduler.core.Scheduler.weekly`

.. _examples.weights.default_behaviour:

Default behaviour
-----------------

By default, the |Scheduler| will prioritize using a linear function
(:py:func:`~scheduler.prioritization.linear_priority_function`) that depends on the
|Job|\ s `weight` and time it is overdue.

.. tip:: It is possible to change the prioritization behaviour of a
    |Scheduler| instance using the `priority_function` argument.
    Details can be found in the guide :ref:`guides.prioritization`.

If several |Job|\ s are scheduled for the same point in time,
they will be executed in order of their weights, starting with the |Job|
of the highest weight:

.. code-block:: pycon

    >>> import datetime as dt
    >>> import time

    >>> from scheduler import Scheduler

    >>> now = dt.datetime.now()
    >>> schedule = Scheduler(max_exec=3)

    >>> for weight in (2, 3, 1, 4):
    ...     job = schedule.once(now, print, weight=weight, kwargs={"end": f"{weight = }\n"})
    ...

    >>> exec_count = schedule.exec_jobs()
    weight = 4
    weight = 3
    weight = 2

    >>> print(schedule)  # doctest:+SKIP
    max_exec=3, tzinfo=None, priority_function=linear_priority_function, #jobs=1
    <BLANKLINE>
    type     function / alias due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    ONCE     print(?)         2021-06-21 03:24:23  -0:00:00           0/1      1

Note that in this example the |Job| with the lowest weight was not
executed, as the execution count per call for the |Scheduler|
has been set to ``3`` via the `max_exec` parameter.

If several |Job|\ s of the same weight are overdue, the
|Job|\ s are prioritized by their delay, starting with the
|Job| of the highest delay.

.. code-block:: pycon

    >>> import datetime as dt
    >>> import time

    >>> from scheduler import Scheduler

    >>> now = dt.datetime.now()
    >>> schedule = Scheduler(max_exec=3)

    >>> for delayed_by in (2, 3, 1, 4):
    ...     exec_time = now - dt.timedelta(seconds=delayed_by)
    ...     job = schedule.once(exec_time, print, kwargs={"end": f"{delayed_by = }s\n"})
    ...

    >>> exec_count = schedule.exec_jobs()
    delayed_by = 4s
    delayed_by = 3s
    delayed_by = 2s

    >>> print(schedule)  # doctest:+SKIP
    max_exec=3, tzinfo=None, priority_function=linear_priority_function, #jobs=1
    <BLANKLINE>
    type     function / alias due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    ONCE     print(?)         2021-06-21 03:24:23  -0:00:00           0/1      1
