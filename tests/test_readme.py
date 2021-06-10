import doctest


# NOTE: We cannot test for the full table, as some Jobs depend on the time of execution
#       e.g. a Job supposed to run on Weekday.MONDAY. The ordering between the Jobs scheduled
#       at 0:09:59 can be guaranteed though, as they differ on the milliseconds level.
def test_general_readme():
    """
    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler, Weekday

    >>> def foo(msg = "bar"):
    ...     print(msg)

    >>> sch = Scheduler()

    Schedule a job that runs every 10 minutes
    >>> sch.schedule(foo, dt.timedelta(minutes=10)) # doctest:+ELLIPSIS
    <scheduler.Job: foo, ..., 0:09:59, 0/inf, weight=1, tzinfo=None>

    Schedule a job that runs every day at 16:45
    >>> sch.schedule(foo, dt.time(hour=16, minute=45)) # doctest:+ELLIPSIS
    <scheduler.Job: foo, ... 16:45:00, ..., 0/inf, weight=1, tzinfo=None>

    Schedule a job that runs every monday at 00:00
    >>> sch.schedule(foo, Weekday.MONDAY) # doctest:+ELLIPSIS
    <scheduler.Job: foo, ... 00:00:00, ..., 0/inf, weight=1, tzinfo=None>

    Schedule a job that runs every monday at 16:45
    >>> sch.schedule(
    ...     foo,
    ...     (Weekday.MONDAY, dt.time(hour=16, minute=45)),
    ... ) # doctest:+ELLIPSIS
    <scheduler.Job: foo, ... 16:45:00, ..., 0/inf, weight=1, tzinfo=None>

    Schedule a job that runs every friday at 00:00, every 10 minutes and every monday at 16:45
    >>> sch.schedule(
    ...     foo,
    ...     [
    ...         Weekday.FRIDAY,
    ...         dt.timedelta(minutes=10),
    ...         (Weekday.MONDAY, dt.time(hour=16, minute=45)),
    ...     ],
    ... ) # doctest:+ELLIPSIS
    <scheduler.Job: foo, ..., 0/inf, weight=1, tzinfo=None>

    Schedule a job at given datetime (here 2021.02.11)
    >>> sch.once(foo, dt.datetime(year=2021, month=2, day=11)) # doctest:+ELLIPSIS
    <scheduler.Job: foo, 2021-02-12 00:00:00, ..., 0/1, weight=1, tzinfo=None>

    Schedule a job in 10 minutes
    >>> sch.once(foo, dt.timedelta(minutes=10)) # doctest:+ELLIPSIS
    <scheduler.Job: foo, ..., 0:09:59, 0/1, weight=1, tzinfo=None>

    Schedule a job in 10000 seconds with parameters
    >>> sch.once(foo, dt.timedelta(seconds=10000), params={"msg": "fizz"}) # doctest:+ELLIPSIS
    <scheduler.Job: foo, ..., 2:46:39, 0/1, weight=1, tzinfo=None>

    Schedule a job that runs every minute with parameters
    >>> sch.schedule(foo, dt.timedelta(minutes=1), params={"msg": "buzz"}) # doctest:+ELLIPSIS
    <scheduler.Job: foo, ..., 0:00:59, 0/inf, weight=1, tzinfo=None>

    >>> print(sch) # doctest:+ELLIPSIS
    max_exec=inf, zinfo=None, #jobs=9, weight_function=linear_weight_function
    <BLANKLINE>
    function               due at           due in      attempts weight       tzinfo
    ---------------- ------------------- --------- ------------- ------ ------------
    ...              ... 0:00:59         0/inf      1         None...
    foo              ... 0:09:59         0/inf      1         None
    foo              ... 0:09:59         0/inf      1         None
    foo              ... 0:09:59           0/1      1         None...
    foo              ... 2:46:39           0/1      1         None
    ...
    <BLANKLINE>

    >>> sch.exec_jobs()
    bar
    1
    """
    DP = doctest.DocTestParser()
    dt_readme = DP.get_doctest(
        test_general_readme.__doc__, globals(), "README", None, None
    )
    DTR = doctest.DocTestRunner()
    assert doctest.TestResults(failed=0, attempted=16) == DTR.run(dt_readme)
