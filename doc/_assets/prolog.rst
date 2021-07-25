.. |br| raw:: html

   <br />

.. |Job| replace:: :py:class:`~scheduler.job.Job`

.. |Scheduler| replace:: :py:class:`~scheduler.core.Scheduler`

.. |JobTimer| replace:: :py:class:`~scheduler.job.JobTimer`

.. |Weekday| replace:: :py:class:`~scheduler.trigger.core.Weekday`

.. |args_text| replace:: Positional argument payload for the function handle |br|
   within a |Job|.

.. |kwargs_text| replace:: Keyword arguments payload for the function handle |br|
   within a |Job|.

.. |tags_text| replace:: A `set` of `str` identifiers for a |Job|.

.. |weight_text| replace:: Relative weight against other
   |Job|\ s.

.. |delay_text| replace:: If ``True`` wait with the execution for the next scheduled |br|
   time.

.. |start_text| replace:: Set the reference `datetime.datetime` stamp the
   |Job| will |br| be scheduled against. |br| Default value
   is `datetime.datetime.now()`.

.. |stop_text| replace:: Define a point in time after which a |Job|
   will be |br| stopped and deleted.

.. |max_attempts_text| replace:: Number of times the |Job| will be
   executed where |br| ``0 <=> inf``. A |Job| with no free attempt
   will be |br| deleted.

.. |skip_missing_text| replace:: If ``True`` a |Job| will only
   schedule it's newest planned |br| execution and drop older ones.