Asyncio
=======

To use `asyncio <https://docs.python.org/3/library/asyncio.html>`_ with the `scheduler` library,
replace the |Scheduler| with the |AsyncScheduler|.
Both schedulers provide nearly the same API and can be exchanged without major adjustments.
The main difference is, that the |AsyncScheduler| works without prioritization and weighting.

The following example shows, how to use the |AsyncScheduler| with a simple coroutine.

.. note:: An ``asyncio`` import is not required.

.. code-block:: pycon

    >>> import datetime as dt
    >>> from scheduler.asyncio import AsyncScheduler

    >>> async def foo():
    ...     print("bar")

    >>> schedule = AsyncScheduler()

    >>> delta = dt.timedelta(minutes=10)
    >>> schedule.cyclic(delta, foo)
    scheduler.asyncio.job.AsyncJob(...CYCLIC...datetime.timedelta(seconds=600)...foo...0,...)

If a customized event loop is required, the second example can be taken into account.

.. code-block:: pycon

    >>> import asyncio
    >>> import datetime as dt
    >>> from scheduler.asyncio import AsyncScheduler

    >>> async def foo():
    ...     print("bar")

    >>> loop = asyncio.get_event_loop()
    >>> schedule = AsyncScheduler(loop=loop)

    >>> delta = dt.timedelta(minutes=10)
    >>> schedule.cyclic(delta, foo)
    scheduler.asyncio.job.AsyncJob(...CYCLIC...datetime.timedelta(seconds=600)...foo...0,...)