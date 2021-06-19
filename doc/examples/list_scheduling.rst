Scheduling of Lists
===================

Sometime it is practical that you can assign several desired times to one :class:`~scheduler.job.Job` `timing`.
This is possible with the help of a `list`.
This feature is available for the functions :func:`~scheduler.core.Scheduler.cyclic`, :func:`~scheduler.core.Scheduler.minutely`,
:func:`~scheduler.core.Scheduler.hourly`, :func:`~scheduler.core.Scheduler.daily` and :func:`~scheduler.core.Scheduler.weekly`.
In the following an example with :func:`~scheduler.core.Scheduler.daily` is shown:

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> def foo():
    ...     print("foo")
    ...
    >>> sch = Scheduler()

    >>> timings = [dt.time(hour=12), dt.time(hour=18), dt.time(hour=0)]
    >>> sch.daily(timing=timings, handle=foo)  # doctest:+ELLIPSIS
    scheduler.Job(...DAILY...)

The source code of the example will create a `Job` that will be executed
three times a day, at given times.