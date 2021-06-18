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
