Job Deletion
============

There are two ways to remove |Job|\ s from a scheduler.

Delete a specific Job by it's reference
---------------------------------------

Setup a couple of |Job|\ s

.. code-block:: pycon

    >>> import datetime as dt
    >>> import time

    >>> from scheduler import Scheduler

    >>> def foo():
    ...     print("foo")

    >>> schedule = Scheduler()
    >>> j1 = schedule.cyclic(dt.timedelta(seconds=1), foo)  # doctest:+ELLIPSIS
    >>> j2 = schedule.cyclic(dt.timedelta(seconds=2), foo)  # doctest:+ELLIPSIS
    >>> j3 = schedule.cyclic(dt.timedelta(seconds=3), foo)  # doctest:+ELLIPSIS
    >>> print(schedule)  # doctest:+SKIP
    max_exec=inf, tzinfo=None, priority_function=linear_priority_function, #jobs=3
    <BLANKLINE>
    type     function / alias due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   foo()            2021-06-20 05:22:29   0:00:00         0/inf      1
    CYCLIC   foo()            2021-06-20 05:22:30   0:00:01         0/inf      1
    CYCLIC   foo()            2021-06-20 05:22:31   0:00:02         0/inf      1
    <BLANKLINE>

Remove the specified |Job| `j2` from the |Scheduler| via
the :py:meth:`~scheduler.core.Scheduler.delete_job` method:

.. code-block:: pycon

    >>> schedule.delete_job(j2)
    >>> print(schedule)  # doctest:+SKIP
    max_exec=inf, tzinfo=None, priority_function=linear_priority_function, #jobs=2
    <BLANKLINE>
    type     function / alias due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   foo()            2021-06-20 05:22:29   0:00:00         0/inf      1
    CYCLIC   foo()            2021-06-20 05:22:31   0:00:02         0/inf      1
    <BLANKLINE>


Delete Jobs
-----------

Setup a couple of |Job|\ s

.. code-block:: pycon

    >>> import datetime as dt
    >>> import time

    >>> from scheduler import Scheduler

    >>> def foo():
    ...     print("foo")

    >>> schedule = Scheduler()
    >>> schedule.cyclic(dt.timedelta(seconds=1), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...CYCLIC...timedelta(seconds=1)...foo...)
    >>> schedule.cyclic(dt.timedelta(seconds=2), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...CYCLIC...timedelta(seconds=2)...foo...)
    >>> schedule.cyclic(dt.timedelta(seconds=3), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...CYCLIC...timedelta(seconds=3)...foo...)
    >>> print(schedule)  # doctest:+SKIP
    max_exec=inf, tzinfo=None, priority_function=linear_priority_function, #jobs=3
    <BLANKLINE>
    type     function / alias due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   foo()            2021-06-20 05:22:29   0:00:00         0/inf      1
    CYCLIC   foo()            2021-06-20 05:22:30   0:00:01         0/inf      1
    CYCLIC   foo()            2021-06-20 05:22:31   0:00:02         0/inf      1
    <BLANKLINE>

Clear the |Scheduler| from |Job|\ s
with a single function call to :py:meth:`~scheduler.core.Scheduler.delete_jobs`.

.. code-block:: pycon

    >>> schedule.delete_jobs()
    3
    >>> print(schedule)  # doctest:+SKIP
    max_exec=inf, tzinfo=None, priority_function=linear_priority_function, #jobs=0
    <BLANKLINE>
    type     function / alias due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    <BLANKLINE>

.. note:: Additionally :py:meth:`~scheduler.core.Scheduler.delete_jobs` supports the
    tagging system described in :ref:`examples.tags`.