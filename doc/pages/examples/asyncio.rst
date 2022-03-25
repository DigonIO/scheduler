Asyncio
=======

To use `asyncio <https://docs.python.org/3/library/asyncio.html>`_ with the `scheduler` library,
replace the default threading Scheduler (:py:class:`scheduler.threading.scheduler.Scheduler`)
with the asyncio Scheduler (:py:class:`scheduler.asyncio.scheduler.Scheduler`) variant.
Both schedulers provide nearly the same API and can be switched out without major adjustments.
The main difference is, that the asyncio |AioScheduler| does not support prioritization and weighting.

The following example shows how to use the asyncio |AioScheduler| with a simple coroutine.

.. code-block:: pycon

    >>> import datetime as dt
    >>> from scheduler.asyncio import Scheduler

    >>> async def foo():
    ...     print("bar")

    >>> schedule = Scheduler()

    >>> delta = dt.timedelta(minutes=10)
    >>> schedule.cyclic(delta, foo)
    scheduler.asyncio.job.Job(...CYCLIC...datetime.timedelta(seconds=600)...foo...0,...)

.. note:: The first example does not require to import ``asyncio``. This only changes once
   a custom event loop is used.

To initialize the |AioScheduler| with a user defined event loop, use the `loop` keyword
argument:

.. code-block:: pycon

    >>> import asyncio
    >>> import datetime as dt
    >>> from scheduler.asyncio import Scheduler

    >>> async def foo():
    ...     print("bar")

    >>> loop = asyncio.get_event_loop()
    >>> schedule = Scheduler(loop=loop)

    >>> delta = dt.timedelta(minutes=10)
    >>> schedule.cyclic(delta, foo)
    scheduler.asyncio.job.Job(...CYCLIC...datetime.timedelta(seconds=600)...foo...0,...)