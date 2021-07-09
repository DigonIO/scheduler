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

    >>> def useful():
    ...     print("Very useful function.")

    >>> tz_new_york = dt.timezone(dt.timedelta(hours=-5))
    >>> tz_wuppertal = dt.timezone(dt.timedelta(hours=2))
    >>> tz_sydney = dt.timezone(dt.timedelta(hours=10))

Next initialize a |Scheduler| with UTC as its reference timezone:

.. code-block:: pycon

    >>> from scheduler import Scheduler, Weekday

    >>> sch = Scheduler(tzinfo=dt.timezone.utc)

Schedule our useful function :func:`~scheduler.core.Scheduler.once` for the current point
in time but using New York local time with:

.. code-block:: pycon

    >>> job_ny = sch.once(dt.datetime.now(tz_new_york), useful)

A daily job running at ``11:45`` local time of Wuppertal can be scheduled with:

.. code-block:: pycon

    >>> job_wu = sch.daily(dt.time(hour=11, minute=45, tzinfo=tz_wuppertal), useful)

Lastly create a job running every Monday at ``10:00`` local time of Sydney as follows:

.. code-block:: pycon

    >>> job_sy = sch.weekly((Weekday.MONDAY, dt.time(hour=10, tzinfo=tz_sydney)), useful)

A simple `print(sch)` statement can be used for an overview of the scheduled
|Job|\ s. As this |Scheduler| instance is timezone
aware, the table contains a `tzinfo` column. Verify if the |Job|\ s are
scheduled as expected.

.. code-block:: pycon

    >>> print(sch)  # doctest:+SKIP
    max_exec=inf, tzinfo=UTC, priority_function=linear_priority_function, #jobs=3
    <BLANKLINE>
    type     function         due at              tzinfo          due in      attempts weight
    -------- ---------------- ------------------- ------------ --------- ------------- ------
    ONCE     useful()         2021-07-01 11:49:49 UTC-05:00     -0:00:00           0/1      1
    DAILY    useful()         2021-07-02 11:45:00 UTC+02:00     16:55:10         0/inf      1
    WEEKLY   useful()         2021-07-05 10:00:00 UTC+10:00       3 days         0/inf      1
    <BLANKLINE>