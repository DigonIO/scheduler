.. |br| raw:: html

   <br />

.. |params_text| replace:: The payload arguments to pass to the function handle |br|
    within a :class:`~scheduler.job.Job`.

.. |weight_text| replace:: Relative weight against other
    :class:`~scheduler.job.Job`\ s.

.. |delay_text| replace:: If ``False`` the :class:`~scheduler.job.Job` will executed
    instantly or at a given |br| offset.

.. |start_text| replace:: Set the reference `datetime.datetime` stamp the
    :class:`~scheduler.job.Job` will |br| be scheduled against. |br| Default value
    is `datetime.datetime.now()`.

.. |stop_text| replace:: Define a point in time after which a :class:`~scheduler.job.Job`
    will be |br| stopped and deleted.

.. |max_attempts_text| replace:: Number of times the :class:`~scheduler.job.Job` will be
    executed where |br| ``0 <=> inf``. A :class:`~scheduler.job.Job` with no free attempt
    will be |br| deleted.

.. |skip_missing_text| replace:: If ``True`` a :class:`~scheduler.job.Job` will only
    schedule it's newest planned |br| execution and drop older ones.