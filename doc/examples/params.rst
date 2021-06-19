Pass parameters
===============

In lots of cases it's necessary to pass parameters to the scheduled callback function.
The keyword `params` provide an easy way to set the desired parameters wrapped in a `dict`.
To highlight this feature the following example show an :func:`~scheduler.core.Scheduler.once` call
without and with parameters.

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> def bar(msg = "bar"):
    ...     print(msg)

    >>> sch = Scheduler()

    >>> _ = sch.once(dt.timedelta(seconds=0.1), bar)
    >>> time.sleep(0.1)
    >>> _ = sch.exec_pending_jobs()
    bar

    >>> _ = sch.once(dt.timedelta(seconds=0.1), bar, params={"msg": "Hello World"})
    >>> time.sleep(0.1)
    >>> _ = sch.exec_pending_jobs()
    Hello World