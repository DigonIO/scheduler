.. |br| raw:: html

   <br />

.. |Job| replace:: :py:class:`~scheduler.job.Job`

.. |Scheduler| replace:: :py:class:`~scheduler.core.Scheduler`

.. |JobTimer| replace:: :py:class:`~scheduler.job.JobTimer`

.. |params_text| replace:: The payload arguments to pass to the function handle |br|
    within a |Job|.

.. |weight_text| replace:: Relative weight against other
    |Job|\ s.

.. |delay_text| replace:: If ``False`` the |Job| will executed
    instantly or at a given |br| offset.

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