Quick Start
===========

To get started with the basic functions and |Job| types of the scheduler
module, create a |Scheduler| instance and the functions `foo` and `bar`
to schedule:

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler, Weekday

    >>> def foo():
    ...     print("foo")

    >>> def bar(msg = "bar"):
    ...     print(msg)

    >>> sch = Scheduler()

Schedule a job that runs every 10 minutes:

.. code-block:: pycon

    >>> sch.cyclic(dt.timedelta(minutes=10), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...CYCLIC...datetime.timedelta(seconds=600)...foo...0, 1...)

Schedule a job that runs every minute at ``XX:XX:15``:

.. code-block:: pycon

    >>> sch.minutely(dt.time(second=15), bar)  # doctest:+ELLIPSIS
    scheduler.Job(...MINUTELY...datetime.time(0, 0, 15)...bar...0, 1...)

Schedule a job that runs every hour at ``XX:30:15``:

.. code-block:: pycon

    >>> sch.hourly(dt.time(minute=30, second=15), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...HOURLY...datetime.time(0, 30, 15)...foo...0, 1...)

Schedule a job that runs every day at ``16:30:00``:

.. code-block:: pycon

    >>> sch.daily(dt.time(hour=16, minute=30), bar)  # doctest:+ELLIPSIS
    scheduler.Job(...DAILY...datetime.time(16, 30)...bar...0, 1...)

Schedule a job that runs every monday at ``00:00``:

.. code-block:: pycon

    >>> sch.weekly(Weekday.MONDAY, foo)  # doctest:+ELLIPSIS
    scheduler.Job(...WEEKLY...MONDAY...foo...0, 1...)

Schedule a job that runs every monday at ``16:30:00``:

.. code-block:: pycon

    >>> sch.weekly((Weekday.MONDAY, dt.time(hour=16, minute=30)), bar)  # doctest:+ELLIPSIS
    scheduler.Job(...WEEKLY...(<Weekday.MONDAY...>, datetime.time(16, 30))...bar...0, 1...)

Schedule a job that runs exactly once in 10 minutes

.. code-block:: pycon

    >>> sch.once(dt.timedelta(minutes=10), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...CYCLIC...datetime.timedelta(seconds=600)...foo...1, 1...)

Schedule a job that runs exactly once next monday at ``00:00``:

.. code-block:: pycon

    >>> sch.once(Weekday.MONDAY, bar)  # doctest:+ELLIPSIS
    scheduler.Job(...WEEKLY...Weekday.MONDAY...bar...1, 1...)

Schedule a job that runs exactly once at the given date at ``2022-02-15 00:45:00``:

.. code-block:: pycon

    >>> sch.once(dt.datetime(year=2022, month=2, day=15, minute=45), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...CYCLIC...foo...1, 1...datetime.datetime(2022, 2, 15, 0, 45)...)

A human readable overview of the scheduled jobs can be created with a simple `print` statement:

.. code-block:: pycon

    >>> print(sch)  # doctest:+SKIP
    max_exec=inf, tzinfo=None, weight_function=linear_priority_function, #jobs=9
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    MINUTELY bar(..)          2021-06-18 00:37:15   0:00:14         0/inf      1
    CYCLIC   foo()            2021-06-18 00:46:58   0:09:58         0/inf      1
    ONCE     foo()            2021-06-18 00:46:59   0:09:58           0/1      1
    HOURLY   foo()            2021-06-18 01:30:15   0:53:14         0/inf      1
    DAILY    bar(..)          2021-06-18 16:30:00  15:52:59         0/inf      1
    WEEKLY   foo()            2021-06-21 00:00:00    2 days         0/inf      1
    ONCE     bar(..)          2021-06-21 00:00:00    2 days           0/1      1
    WEEKLY   bar(..)          2021-06-21 16:30:00    3 days         0/inf      1
    ONCE     foo()            2022-02-15 00:45:00  242 days           0/1      1
    <BLANKLINE>

Unless |Scheduler| was given a limit on the execution count via the `max_exec` option, a call to
the Scheduler instances :meth:`~scheduler.core.Scheduler.exec_jobs` function will execute every
overdue job exactly once.

.. code-block:: pycon

    >>> sch.exec_jobs()  # doctest:+SKIP

For cyclic execution of |Job|\ s, the :meth:`~scheduler.core.Scheduler.exec_jobs` function should
be embedded in a loop of the host program:

.. code-block:: pycon

    >>> while True:  # doctest:+SKIP
    ...     sch.exec_jobs()
    ...     time.sleep(1)
