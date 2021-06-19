Job deletion
============
Two ways to delete :class:`~scheduler.job.Job`\ s...

Delete a Job by it's reference
------------------------------

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> def foo():
    ...     print("foo")

    >>> sch = Scheduler()
    >>> job = sch.cyclic(dt.timedelta(seconds=1), foo)

    >>> sch.delete_job(job)

Delete all Jobs
---------------

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> def foo():
    ...     print("foo")

    >>> sch = Scheduler()
    >>> _ = sch.cyclic(dt.timedelta(seconds=1), foo)
    >>> _ = sch.cyclic(dt.timedelta(seconds=2), foo)
    >>> _ = sch.cyclic(dt.timedelta(seconds=3), foo)

    >>> sch.delete_jobs()