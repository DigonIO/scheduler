Examples
--------

`Job` scheduling and oneshot `Job`\ s
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The basic functions and `Job` types of the scheduler module are explained below.
First, it is shown how cyclic `Job`\ s can be created and how the desired execution
times can be selected and combined.
Furthermore, oneshot jobs are introduced, whereby oneshot `Job`\ s explicitly
accept a date and a time as parameters in addition to the desired execution times.

Create a `Scheduler` instance:

>>> import time
>>> import datetime as dt
>>> from scheduler import Scheduler, Weekday
...
>>> def foo():
...     print("bar")
...
>>> sch = Scheduler(tzinfo=dt.timezone.utc)

Schedule a `Job` for execution every 10 minutes ...

>>> sch.schedule(foo, dt.timedelta(minutes=10)) # doctest:+ELLIPSIS
<scheduler.job.Job object at 0x...>

Schedule a `Job` for execution every day at 16:45 ...

>>> sch.schedule(foo, dt.time(hour=16, minute=45)) # doctest:+ELLIPSIS
<scheduler.job.Job object at 0x...>

Schedule a `Job` every monday at 00:00 ...

>>> sch.schedule(foo, Weekday.MONDAY) # doctest:+ELLIPSIS
<scheduler.job.Job object at 0x...>

Schedule a `Job` every monday at 16:45 ...

>>> sch.schedule(
...     foo,
...     (Weekday.MONDAY, dt.time(hour=16, minute=45)),
... ) # doctest:+ELLIPSIS
<scheduler.job.Job object at 0x...>

Schedule a `Job` every friday at 00:00, every 10 minutes and every monday at 16:45 ...

>>> sch.schedule(
...     foo,
...     [
...         Weekday.FRIDAY,
...         dt.timedelta(minutes=10),
...         (Weekday.MONDAY, dt.time(hour=16, minute=45)),
...     ],
... ) # doctest:+ELLIPSIS
<scheduler.job.Job object at 0x...>

Schedule a oneshot `Job` for the next monday at 00:00 ...

>>> sch.once(foo, Weekday.MONDAY) # doctest:+ELLIPSIS
<scheduler.job.Job object at 0x...>

Schedule a oneshot `Job` for a specific date and time ...

>>> sch.once(foo, dt.datetime(year=2021, month=5, day=27, hour=3, minute=23)) # doctest:+ELLIPSIS
<scheduler.job.Job object at 0x...>

In order to execute the `Job`\ s, the corresponding function
`Scheduler.exec_jobs()` must be called cyclically.
This should be embedded in a loop in the host program.

How to use time zones
^^^^^^^^^^^^^^^^^^^^^

With the time zone support of the `datetime` library,
`scheduler` is also able to observe time zones. The following
example outlines how to use time zones (please note that as
soon as a `Scheduler` is instantiated with a time zone, all other
`datetime` objects that are passed must also be provided with time zones):

>>> import time
>>> import datetime as dt
>>> from scheduler import Scheduler, Weekday
...
>>> sch = Scheduler(tzinfo=dt.timezone.utc)
...
>>> _ = sch.once(lambda: None, dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=10))
>>> _ = sch.schedule(lambda: None, dt.timedelta(seconds=10))
>>> _ = sch.schedule(lambda: None, Weekday.MONDAY)
>>> _ = sch.schedule(lambda: None, dt.time(hour=1, minute=1, tzinfo=dt.timezone.utc))

Weights
^^^^^^^

`Job`\ s can be weighted among each other.
This becomes more relevant the longer the execution of a
`Job` is compared to the cycle length of the `Scheduler`.
It may be that the `Job`\ s to be executed take longer than one
cycle of the `Scheduler`. In order to enable a constant frequency,
the maximum number of `Job`\ s to be executed can be limited.
This is illustrated in the following example with the help of
oneshot `Job`\ s, but is also possible with normal `Job`\ s:

>>> import time
>>> import datetime as dt
>>> from scheduler import Scheduler
...
>>> exec_at = dt.datetime.now() + dt.timedelta(seconds=1)
...
>>> sch = Scheduler(max_exec=3)
>>> _ = sch.once(lambda: print("Weight 2"), exec_at, weight=2)
>>> _ = sch.once(lambda: print("Weight 3"), exec_at, weight=3)
>>> _ = sch.once(lambda: print("Weight 1"), exec_at, weight=1)
>>> _ = sch.once(lambda: print("Weight 4"), exec_at, weight=4)

If the `Job`\ s are now executed, only 3 of 4 `Job`\ s are processed.
Note that a `Job` in the next cycle is now one execution behind,
this can increase permanently depending on the situation and
the `Job` cannot finish all overdue executions.

>>> time.sleep(1)
>>> print(sch.exec_jobs())
Weight 4
Weight 3
Weight 2
3

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

>>> print(job.max_attemps, job.attemps ,job.has_attempts)
2 0 True

>>> time.sleep(1)
>>> print(sch.exec_jobs())
1
>>> print(job.max_attemps, job.attemps ,job.has_attempts)
2 1 True

>>> time.sleep(1)
>>> print(sch.exec_jobs())
1
>>> print(job.max_attemps, job.attemps ,job.has_attempts)
2 2 False