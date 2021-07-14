Metrics
=======

The |Scheduler| and |Job| classes
provide access to various metrics that can be of interest for the using program.

Starting with a |Scheduler| and two |Job|\ s:

.. code-block:: pycon

    >>> import time
    >>> import datetime as dt
    >>> from scheduler import Scheduler

    >>> def foo():
    ...     print("foo")

    >>> sch = Scheduler()
    >>> job = sch.once(dt.timedelta(minutes=10), foo)
    >>> print(sch)  # doctest:+SKIP
    max_exec=inf, tzinfo=None, priority_function=linear_priority_function, #jobs=2
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    ONCE     foo()            2021-06-21 04:53:34   0:09:59           0/1      1

|Scheduler| provides access to the set of |Job|\ s stored with the `jobs`
We can access the |Job|\ s of the scheduler via the :py:attr:`~scheduler.core.Scheduler.jobs` property.

.. code-block:: pycon

    >>> sch.jobs == {job}
    True

For the |Job| with the following string representation

.. code-block:: pycon

    >>> print(job)  # doctest:+SKIP
    ONCE, foo(), at=2021-06-21 04:53:34, tz=None, in=0:09:59, #0/1, w=1.000

The scheduled :py:attr:`~scheduler.job.Job.datetime` and :py:attr:`~scheduler.job.Job.timedelta`
informations can directly be accessed and might look like similar to what is listed below:

.. code-block:: pycon

    >>> print(f"{job.datetime = !s}\n{job.timedelta() = !s}")  # doctest:+SKIP
    job.datetime = 2021-06-21 04:53:34.879346
    job.timedelta() = 0:09:59.999948

These metrics can change during the |Job|\ s lifetime. We can exemplify this
for the :py:attr:`~scheduler.job.Job.attempts` attribute:

.. code-block:: pycon

    >>> job = sch.cyclic(dt.timedelta(seconds=0.1), foo, max_attempts=2, delay=False)
    >>> print(job)  # doctest:+SKIP
    CYCLIC, foo(), at=2021-06-21 04:53:34, tz=None, in=0:00:00, #0/2, w=1.000

    >>> print(job.attempts, job.max_attempts)
    0 2

    >>> time.sleep(0.1)
    >>> exec_count = sch.exec_jobs()
    foo

    >>> print(job.attempts, job.max_attempts)
    1 2

    >>> time.sleep(0.1)
    >>> exec_count = sch.exec_jobs()
    foo

    >>> print(job.attempts, job.max_attempts)
    2 2