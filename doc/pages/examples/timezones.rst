Timezones
=========

The `scheduler` library supports timezones via the standard `datetime` library.

.. warning:: **Mixing of offset-naive and offset-aware** `datetime.time` **and**
    `datetime.datetime` **objects is not supported.**

    If a |Scheduler| is initialized with a timezone, all `datetime.time`, `datetime.datetime` and
    |Job| objects require timezones.
    Vice versa a |Scheduler| without timezone informations does not support
    `datetime` or |Job| objects with timezones.

For demonstration purposes, we will create a |Scheduler| with
|Job|\ s defined in different timezones of the world.

First create the timezones of a few known cities and a useful function to schedule.

.. code-block:: pycon

    >>> import datetime as dt
    >>> from zoneinfo import ZoneInfo

    >>> def useful():
    ...     print("Very useful function.")
    ...

    >>> tz_berlin = ZoneInfo("Europe/Berlin")
    >>> tz_new_york = ZoneInfo("America/New_York")
    >>> tz_sydney = ZoneInfo("Australia/Sydney")
    >>> tz_const = dt.timezone(offset=dt.timedelta(hours=2))

Next initialize a |Scheduler| with UTC as its reference timezone:

.. code-block:: pycon

    >>> from scheduler import Scheduler
    >>> import scheduler.trigger as trigger

    >>> schedule = Scheduler(tzinfo=dt.timezone.utc)

Schedule our useful function :py:func:`~scheduler.core.Scheduler.once` for the current point
in time but using Berlin local time with:

.. code-block:: pycon

    >>> job_be = schedule.once(dt.datetime.now(tz_berlin), useful)

A daily job running at ``11:45`` local time of New York can be scheduled with:

.. code-block:: pycon

    >>> job_ny = schedule.daily(dt.time(hour=11, minute=45, tzinfo=tz_new_york), useful)

To create a job running every Monday at ``10:00`` local time of Sydney as follows:

.. code-block:: pycon

    >>> job_sy = schedule.weekly(trigger.Monday(dt.time(hour=10, tzinfo=tz_sydney)), useful)

Lastly use the constant UTC offset without daylight saving time (DST) to schedule a daily job at ``12:00``:

.. code-block:: pycon

    >>> job_co = schedule.daily(dt.time(hour=12, tzinfo=tz_const), useful)

A simple `print(schedule)` statement can be used for an overview of the scheduled
|Job|\ s. As this |Scheduler| instance is timezone
aware, the table contains a `tzinfo` column. Verify if the |Job|\ s are
scheduled as expected.

.. code-block:: pycon

    >>> print(schedule)  # doctest:+SKIP
    max_exec=inf, tzinfo=UTC, priority_function=linear_priority_function, #jobs=4
    <BLANKLINE>
    type     function / alias due at              tzinfo          due in      attempts weight
    -------- ---------------- ------------------- ------------ --------- ------------- ------
    ONCE     useful()         2026-02-15 22:22:57 CET           -0:00:05           0/1      1
    WEEKLY   useful()         2026-02-16 10:00:00 AEDT           1:36:57         0/inf      1
    DAILY    useful()         2026-02-16 12:00:00 UTC+02:00     12:36:57         0/inf      1
    DAILY    useful()         2026-02-16 11:45:00 EST           19:21:57         0/inf      1
    <BLANKLINE>
