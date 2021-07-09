Job Deletion
============

There are two ways to remove |Job|\ s from a scheduler.

Delete a specific Job by it's reference
---------------------------------------

Setup a couple of |Job|\ s

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> def foo():
    ...     print("foo")

    >>> sch = Scheduler()
    >>> j1 = sch.cyclic(dt.timedelta(seconds=1), foo)  # doctest:+ELLIPSIS
    >>> j2 = sch.cyclic(dt.timedelta(seconds=2), foo)  # doctest:+ELLIPSIS
    >>> j3 = sch.cyclic(dt.timedelta(seconds=3), foo)  # doctest:+ELLIPSIS
    >>> print(sch)  # doctest:+SKIP
    max_exec=inf, timezone=None, weight_function=linear_priority_function, #jobs=3
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   foo()            2021-06-20 05:22:29   0:00:00         0/inf      1
    CYCLIC   foo()            2021-06-20 05:22:30   0:00:01         0/inf      1
    CYCLIC   foo()            2021-06-20 05:22:31   0:00:02         0/inf      1
    <BLANKLINE>

Remove the specified |Job| `j2` from the |Scheduler| via
the :meth:`~scheduler.core.Scheduler.delete_job` method:

.. code-block:: pycon

    >>> sch.delete_job(j2)
    >>> print(sch)  # doctest:+SKIP
    max_exec=inf, timezone=None, weight_function=linear_priority_function, #jobs=2
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   foo()            2021-06-20 05:22:29   0:00:00         0/inf      1
    CYCLIC   foo()            2021-06-20 05:22:31   0:00:02         0/inf      1
    <BLANKLINE>


Delete all Jobs
---------------

Setup a couple of |Job|\ s

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> def foo():
    ...     print("foo")

    >>> sch = Scheduler()
    >>> sch.cyclic(dt.timedelta(seconds=1), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...CYCLIC...timedelta(seconds=1)...foo...)
    >>> sch.cyclic(dt.timedelta(seconds=2), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...CYCLIC...timedelta(seconds=2)...foo...)
    >>> sch.cyclic(dt.timedelta(seconds=3), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...CYCLIC...timedelta(seconds=3)...foo...)
    >>> print(sch)  # doctest:+SKIP
    max_exec=inf, timezone=None, weight_function=linear_priority_function, #jobs=3
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   foo()            2021-06-20 05:22:29   0:00:00         0/inf      1
    CYCLIC   foo()            2021-06-20 05:22:30   0:00:01         0/inf      1
    CYCLIC   foo()            2021-06-20 05:22:31   0:00:02         0/inf      1
    <BLANKLINE>

Clear the |Scheduler| from |Job|\ s
with a single function call to :meth:`~scheduler.core.Scheduler.delete_all_jobs`.

.. code-block:: pycon

    >>> sch.delete_all_jobs()
    >>> print(sch)  # doctest:+SKIP
    max_exec=inf, timezone=None, weight_function=linear_priority_function, #jobs=0
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    <BLANKLINE>