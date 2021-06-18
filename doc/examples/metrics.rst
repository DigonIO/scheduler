Metrics
^^^^^^^

The `Scheduler` and the `Job`\ s give the user feedback on
their status via various metrics. They can be found in the
documentation of the individual objects.

In the following example the number of times a job can be
executed is limited. The metrics are displayed to observe
their change.

>>> import time
>>> import datetime as dt
>>> from scheduler import Scheduler
...
>>> sch = Scheduler()
...
>>> job = sch.schedule(lambda: None, dt.timedelta(seconds=1), max_attempts=2, delay=False)

>>> print(job.max_attemps, job.attemps)
2 0

>>> time.sleep(1)
>>> print(sch.exec_jobs())
1
>>> print(job.max_attemps, job.attemps)
2 1

>>> time.sleep(1)
>>> print(sch.exec_jobs())
1
>>> print(job.max_attemps, job.attemps)
2 2