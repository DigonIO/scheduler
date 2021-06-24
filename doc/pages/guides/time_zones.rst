Time Zones
==========

In this guide we will deal with the functionality of time zones.
The `scheduler` library has a time zone support which is based on the functions of the
standard `datetime` library.

In the `datetime` library there is an important rule
when you want to work with time zones,
you can not work with offset-naive and offset-aware `datetime` objects at the same time.
As a result, as soon as a :class:`~scheduler.core.Scheduler` is initialized with a time zone,
the following `datetime` objects must always be provided with a time zone:
:class:`datetime.datetime`,
:class:`datetime.time`.
However, if you use the :class:`datetime.timedelta` or :class:`~scheduler.util.Weekday` objects
no time zone can be specified and the time zone of the `Scheduler`
will be used automatically.

If you consider this restriction, it provides the possibility to schedule `Job`\ s in different
time zones of the world and independent from each other.
To demonstrate this feature, let's first create the time zones of a few known cities and the time zone UTC.

.. code-block:: pycon

    >>> import datetime as dt

    >>> tz_new_york = dt.timezone(dt.timedelta(hours=-5))
    >>> tz_wuppertal = dt.timezone(dt.timedelta(hours=2))
    >>> tz_sydney = dt.timezone(dt.timedelta(hours=10))
    >>> tz_utc = dt.timezone.utc

Now we import the `Scheduler` and pass it the UTC time zone as its reference time zone.
The also imported `Weekday` will be needed in a moment.
Additionally we implement a usfull function that we can pass to the `Job`\ s.

.. code-block:: pycon

    >>> from scheduler import Scheduler, Weekday
    >>> sch = Scheduler(tzinfo=tz_utc)

    >>> def usefull():
    ...     print("Very usefull function.")

First, we would like to plan our very useful function in the time zone of New York once.
For this purpose, scheduling via :func:`~scheduler.core.Scheduler.once` is suitable,
taking into consideration passing the time zone `tz_new_york` to the function
:func:`datetime.datetime.now`:

.. code-block:: pycon

    >>> _ = sch.once(dt.datetime.now(tz_new_york), usefull)

The next time we need the functionality of our useful function in the time zone
of Wuppertal. We plan a daily execution at ``11:45``, this time the timezone is `tz_wuppertal`.

.. code-block:: pycon

    >>> _ = sch.daily(dt.time(hour=11, minute=45, tzinfo=tz_wuppertal), usefull)

Lastly, we plan to use our so useful functions in Sydney with the time zone `tz_sydney`.
We would like to run the functions every Monday at ``10:00``.

.. code-block:: pycon

    >>> _ = sch.weekly((Weekday.MONDAY, dt.time(hour=10, tzinfo=tz_sydney)), usefull)

To see if the time zones were taken over correctly we verify this with a simple `print(sch)` statement.
If a time zone is passed to the `Scheduler` the table automatically gets the column `timezone`.
In this column the time zones of the single `Job`\ s are displayed.

.. code-block:: pycon

    >>> print(sch)  # doctest:+ELLIPSIS
    max_exec=inf, timezone=UTC, priority_function=linear_priority_function, #jobs=3
    <BLANKLINE>
    type     function         due at              timezone        due in      attempts weight
    -------- ---------------- ------------------- ------------ --------- ------------- ------
    ONCE     usefull()        ...                 UTC-05:00          ...           0/1      1
    DAILY    usefull()        ...                 UTC+02:00          ...         0/inf      1
    WEEKLY   usefull()        ...                 UTC+10:00          ...         0/inf      1