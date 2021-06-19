Metrics
^^^^^^^

The :class:`~scheduler.core.Scheduler` and :class:`~scheduler.job.Job` classes
provide various metrics to give feedback of their status to the user.
A complete overview can be found in the API References of the respective objects.


In the following example the number of times a job can be executed is limited.
The metrics are displayed to observe their change.

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler
    ...
    >>> def foo():
    ...     print("foo")
    ...
    >>> sch = Scheduler()
    ...
    >>> job = sch.cyclic(dt.timedelta(seconds=1), foo, max_attempts=2, delay=False)
    >>> print(job.max_attemps, job.attemps)
    2 0
    >>> time.sleep(1)
    >>> count = sch.exec_pending_jobs()
    foo
    >>> count
    1
    >>> print(job.max_attemps, job.attemps)
    2 1

    >>> time.sleep(1)
    >>> count = sch.exec_pending_jobs()
    foo
    >>> count
    1
    >>> print(job.max_attemps, job.attemps)
    2 2