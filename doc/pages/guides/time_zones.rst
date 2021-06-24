Time Zones
==========

With the time zone support of the `datetime` library,
`scheduler` is also able to observe time zones. The following
example outlines how to use time zones (please note that as
soon as a `Scheduler` is instantiated with a time zone, all other
`datetime` objects that are passed must also be provided with time zones):

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler, Weekday
    ...
    >>> def foo():
    ...     print("foo")
    ...
    >>> sch = Scheduler(tzinfo=dt.timezone.utc)
    ...
    >>> sch.once(dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=10), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...CYCLIC...timedelta(0)...foo...1, 1...datetime.datetime(...utc)...utc)
    >>> sch.cyclic(dt.timedelta(seconds=10), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...CYCLIC...timedelta(seconds=10)...foo...0, 1...datetime.datetime(...utc)...utc)
    >>> sch.weekly(Weekday.MONDAY, foo)  # doctest:+ELLIPSIS
    scheduler.Job(...WEEKLY...MONDAY...foo...0, 1...datetime.datetime(...utc)...utc)
    >>> sch.daily(dt.time(hour=1, minute=1, tzinfo=dt.timezone.utc), foo)  # doctest:+ELLIPSIS
    scheduler.Job(...DAILY...time(1, 1, ...utc)...foo...0, 1...datetime.datetime(...utc)...utc)
