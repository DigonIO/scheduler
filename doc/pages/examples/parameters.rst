Parameter Forwarding
====================

It is possible to forward parameters to the the scheduled callback function via the `params` argument.
It accepts a dictionary with strings referencing the callback function's arguments and is available
for all scheduling functions of |Scheduler|:

:func:`~scheduler.core.Scheduler.once`,
:func:`~scheduler.core.Scheduler.cyclic`,
:func:`~scheduler.core.Scheduler.minutely`,
:func:`~scheduler.core.Scheduler.hourly`,
:func:`~scheduler.core.Scheduler.daily`,
:func:`~scheduler.core.Scheduler.weekly`

In the following example we schedule two |Job|\ s via
:func:`~scheduler.core.Scheduler.once`. The first |Job| exhibits the function's default behaviour.
Whereas the second |Job| prints the modified message defined in the `kwargs` argument.

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> def bar(msg = "bar"):
    ...     print(msg)

    >>> sch = Scheduler()

    >>> sch.once(dt.timedelta(seconds=0.1), bar)  # doctest:+ELLIPSIS
    scheduler.Job(...timedelta(microseconds=100000)...bar...)

    >>> time.sleep(0.1)
    >>> n_exec = sch.exec_jobs()
    bar

    >>> sch.once(dt.timedelta(seconds=0.1), bar, kwargs={"msg": "Hello World"})
    scheduler.Job(...timedelta(microseconds=100000)...bar...{'msg': 'Hello World'}...)

    >>> time.sleep(0.1)
    >>> n_exec = sch.exec_jobs()
    Hello World