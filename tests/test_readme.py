import doctest
import pytest

# NOTE: We cannot test for the full table, as some Jobs depend on the time of execution
#       e.g. a Job supposed to run on Weekday.MONDAY. The ordering between the Jobs scheduled
#       at 0:09:59 can be guaranteed though, as they differ on the milliseconds level.
# NOTE: Currently when updating the example in the README.md file, the changes should be applied
#       manually in this file as well.
# NOTE: The same example and doctest can be found in `doc/examples/general_job_scheduling.rst`,
#       however here the test is more granular, wheras in `doc/examples` the focus is more on
#       readability and additional comments.
def test_general_readme():
    r"""
    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler, Weekday

    >>> def foo():
    ...     print("foo")

    >>> def bar(msg = "bar"):
    ...     print(msg)

    >>> sch = Scheduler()

    Schedule a job that runs every 10 minutes:
    >>> sch.cyclic(dt.timedelta(minutes=10), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.CYCLIC...>, datetime.timedelta(seconds=600), <function foo at 0x...>, {}, 0, 1, True, datetime.datetime(...), None, False, None)

    Schedule a job that runs every minute at ``XX:XX:15``:
    >>> sch.minutely(dt.time(second=15), bar)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.MINUTELY...>, datetime.time(0, 0, 15), <function bar at 0x...>, {}, 0, 1, True, datetime.datetime(...), None, False, None)

    Schedule a job that runs every hour at ``XX:30:15``:
    >>> sch.hourly(dt.time(minute=30, second=15), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.HOURLY...>, datetime.time(0, 30, 15), <function foo at 0x...>, {}, 0, 1, True, datetime.datetime(...), None, False, None)

    Schedule a job that runs every day at ``16:30:00``:
    >>> sch.daily(dt.time(hour=16, minute=30), bar)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.DAILY...>, datetime.time(16, 30), <function bar at 0x...>, {}, 0, 1, True, datetime.datetime(...), None, False, None)

    Schedule a job that runs every monday at ``00:00``:
    >>> sch.weekly(Weekday.MONDAY, foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.WEEKLY...>, <Weekday.MONDAY...>, <function foo at 0x...>, {}, 0, 1, True, datetime.datetime(...), None, False, None)

    Schedule a job that runs every monday at ``16:30:00``:
    >>> sch.weekly((Weekday.MONDAY, dt.time(hour=16, minute=30)), bar)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.WEEKLY...>, (<Weekday.MONDAY...>, datetime.time(16, 30)), <function bar at 0x...>, {}, 0, 1, True, datetime.datetime(...), None, False, None)

    Schedule a job that runs exactly once in 10 minutes
    >>> sch.once(dt.timedelta(minutes=10), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.CYCLIC...>, datetime.timedelta(seconds=600), <function foo at 0x...>, {}, 1, 1, True, datetime.datetime(...), None, False, None)

    Schedule a job that runs exactly once next monday at ``00:00``:
    >>> sch.once(Weekday.MONDAY, bar)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.WEEKLY...>, <Weekday.MONDAY...>, <function bar at 0x...>, {}, 1, 1, True, datetime.datetime(...), None, False, None)

    Schedule a job that runs exactly once at the given date at ``2022-02-15 00:45:00``:
    >>> sch.once(dt.datetime(year=2022, month=2, day=15, minute=45), foo)  # doctest:+ELLIPSIS
    scheduler.Job(<JobType.CYCLIC...>, datetime.timedelta(0), <function foo at 0x...>, {}, 1, 1, False, datetime.datetime(2022, 2, 15, 0, 45), None, False, None)

    >>> print(sch)  # doctest:+ELLIPSIS
    max_exec=inf, timezone=None, weight_function=linear_weight_function, #jobs=9
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    ...
    DAILY    bar(..)          2021-06-18 16:30:00  ...         0/inf      1
    ...
    <BLANKLINE>

    Unless `Scheduler` was not given a limit on the execution count via `max_exec`, a call to
    the Scheduler instances `exec_pending_jobs()` function will execute every overdue job exactly once.

    >>> sch.exec_pending_jobs()  # doctest:+SKIP

    For cyclic execution of `Job`\ s, the `exec_pending_jobs()` function should be embedded in a loop of
    the host program. E.g.:

    >>> while True:  # doctest:+SKIP
    ...     sch.exec_pending_jobs()
    ...     time.sleep(1)
    """
    DP = doctest.DocTestParser()
    dt_readme = DP.get_doctest(
        test_general_readme.__doc__, globals(), "README", None, None
    )
    DTR = doctest.DocTestRunner()
    assert doctest.TestResults(failed=0, attempted=16) == DTR.run(dt_readme)
