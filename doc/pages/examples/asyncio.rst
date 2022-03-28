Asyncio
=======

To use `asyncio <https://docs.python.org/3/library/asyncio.html>`_ with the `scheduler` library,
replace the default threading Scheduler (:py:class:`scheduler.threading.scheduler.Scheduler`)
with the asyncio Scheduler (:py:class:`scheduler.asyncio.scheduler.Scheduler`) variant.
Both schedulers provide a nearly identical API - the only difference is the lack of
prioritization and weighting support for the asyncio |AioScheduler|.

.. note:: In contrast to the threading |Scheduler| it is necessary to instanciate
   the asyncio |AioScheduler| within a coroutine.

The following example shows how to use the asyncio |AioScheduler| with a simple coroutine.

.. code-block:: python

  import asyncio
  import datetime as dt

  from scheduler.asyncio import Scheduler

  async def foo():
      print("foo")

  async def main():
      schedule = Scheduler()

      schedule.once(dt.timedelta(seconds=5), foo)
      schedule.cyclic(dt.timedelta(minutes=10), foo)

      while True:
          await asyncio.sleep(1)

  asyncio.run(main())


To initialize the |AioScheduler| with a user defined event loop, use the `loop` keyword
argument:

.. code-block:: python

  import asyncio
  import datetime as dt

  from scheduler.asyncio import Scheduler

  async def foo():
      print("foo")

  async def main():
      loop = asyncio.get_running_loop()
      schedule = Scheduler(loop=loop)

      schedule.once(dt.timedelta(seconds=5), foo)
      schedule.cyclic(dt.timedelta(minutes=10), foo)

      while True:
          await asyncio.sleep(1)

  asyncio.run(main())