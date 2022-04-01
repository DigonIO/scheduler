.. |br| raw:: html

   <br />

.. |BaseJob| replace:: :py:class:`~scheduler.base.job.BaseJob`

.. |BaseScheduler| replace:: :py:class:`~scheduler.base.scheduler.BaseScheduler`

.. |Job| replace:: :py:class:`~scheduler.threading.job.Job`

.. |Scheduler| replace:: :py:class:`~scheduler.threading.scheduler.Scheduler`

.. |AioJob| replace:: :py:class:`~scheduler.asyncio.job.Job`

.. |AioScheduler| replace:: :py:class:`~scheduler.asyncio.scheduler.Scheduler`

.. |JobTimer| replace:: :py:class:`~scheduler.base.job_timer.JobTimer`

.. |Weekday| replace:: :py:class:`~scheduler.trigger.core.Weekday`

.. |args_text| replace:: Positional argument payload for the function handle within a |Job|.

.. |kwargs_text| replace:: Keyword arguments payload for the function handle within a |Job|.

.. |tags_text| replace:: A `set` of `str` identifiers for a |Job|.

.. |weight_text| replace:: Relative weight against other |Job|\ s.

.. |delay_text| replace:: *Deprecated*: If ``True`` wait with the execution for
   the next scheduled time.

.. |start_text| replace:: Set the reference `datetime.datetime` stamp the
   |Job| will be scheduled against. Default value is `datetime.datetime.now()`.

.. |stop_text| replace:: Define a point in time after which a |Job|
   will be stopped and deleted.

.. |max_attempts_text| replace:: Number of times the |Job| will be
   executed where ``0 <=> inf``. A |Job| with no free attempt
   will be deleted.

.. |skip_missing_text| replace:: If ``True`` a |Job| will only
   schedule it's newest planned execution and drop older ones.

.. |alias_text| replace:: Set the timezone of the |AioScheduler| the |AioJob|
   is scheduled in.