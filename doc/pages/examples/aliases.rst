.. _examples.aliases:

Aliases
=======

By default a job is represented by its :py:class:`~scheduler.definition.JobType`
and function handle. If multiple jobs are scheduled that have identical type and handle,
it can be difficult to distinguish between these.



The example below shows how a hypothetical function for ordering goods is reused and
cannot be uniquely identified in the table below for the given orders.

.. code-block:: pycon

   >>> import datetime as dt

   >>> from scheduler import Scheduler

   >>> def order(unit):
   ...     print(f"ordering {unit} units")

   >>> schedule = Scheduler()

   >>> job1 = schedule.cyclic(dt.timedelta(seconds=1), order, args=(2,))
   >>> job2 = schedule.cyclic(dt.timedelta(seconds=1), order, args=(9,))
   >>> print(schedule)  # doctest:+SKIP
   max_exec=inf, tzinfo=None, priority_function=linear_priority_function, #jobs=2
   <BLANKLINE>
   type     function / alias due at                 due in      attempts weight
   -------- ---------------- ------------------- --------- ------------- ------
   CYCLIC   order()          2022-05-04 14:51:25   0:00:00         0/inf      1
   CYCLIC   order()          2022-05-04 14:51:26   0:00:00         0/inf      1
   <BLANKLINE>

To avoid confusion in the job representation, use the :attr:`~scheduler.base.job.BaseJob.alias`
keyword as listed below:

.. code-block:: pycon

   >>> schedule = Scheduler()

   >>> job1 = schedule.cyclic(dt.timedelta(seconds=1), order, alias='small order', args=(2,))
   >>> job2 = schedule.cyclic(dt.timedelta(seconds=2), order, alias='medium order', args=(9,))
   >>> print(schedule)  # doctest:+SKIP
   max_exec=inf, tzinfo=None, priority_function=linear_priority_function, #jobs=2
   <BLANKLINE>
   type     function / alias due at                 due in      attempts weight
   -------- ---------------- ------------------- --------- ------------- ------
   CYCLIC   small order      2022-05-04 14:54:33   0:00:00         0/inf      1
   CYCLIC   medium order     2022-05-04 14:54:34   0:00:00         0/inf      1
   <BLANKLINE>

.. note:: This feature is available for both, the default threading |Scheduler| and the asyncio
   |AioScheduler|.
