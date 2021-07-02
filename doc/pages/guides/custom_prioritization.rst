Custom Prioritization
=====================

We previously discussed the default :class:`~scheduler.job.Job` prioritization behaviour
in the :ref:`examples.weights` example.

By default the priority in :class:`~scheduler.core.Scheduler` is computed using the
:func:`~scheduler.util.linear_priority_function`, where :math:`\mathtt{time\_delta}` is
defined as the difference between the current time (:math:`\mathtt{now}`) and the
planned execution time (:math:`\mathtt{next\_exec}`) with
:math:`\mathtt{time\_delta}=\mathtt{now}-\mathtt{next\_exec}`.
The default :func:`~scheduler.util.linear_priority_function` implements the prioritization
using the following formula:

.. math::
    \left(\mathtt{time\_delta},\mathtt{weight}\right)\ {\mapsto}\begin{cases}
    0 & :\ \mathtt{time\_delta}<0\\
    {\left(\mathtt{time\_delta}+1\right)}\cdot\mathtt{weight} & :\ \mathtt{time\_delta}\geq0
    \end{cases}

.. note:: By default :class:`~scheduler.job.Job`\ s with a priority value smaller or
    equal to zero are not executed by the :meth:`~scheduler.core.Scheduler.exec_jobs`
    method of the :class:`~scheduler.core.Scheduler`.

Some applications require customized prioritization models (e.g. with quadratic or exponential
behaviour). Each :class:`~scheduler.core.Scheduler` instance supports a custom implementation
of the prioritization function.

.. note:: The custom prioritization functions implemented in this guide are directly
    available from :class:`~scheduler.util.Prioritization`.

Constant Weight Prioritization
------------------------------

In this example we are going to implement a priority function without the time linear behaviour
of the default :func:`~scheduler.util.linear_priority_function` with:

.. math::
    \left(\mathtt{time\_delta},\mathtt{weight}\right)\ {\mapsto}\begin{cases}
    0 & :\ \mathtt{time\_delta}<0\\
    \mathtt{weight} & :\ \mathtt{time\_delta}\geq0
    \end{cases}

The :class:`~scheduler.core.Scheduler` expects a prioritization function of the signature
``Callable[[float, Job, int, int], float]``. The custom prioritization function is
available in :mod:`~scheduler.util` as :meth:`~scheduler.util.Prioritization.constant_weight_prioritization`.

.. code-block:: python

    import scheduler

    def constant_weight_prioritization(
        time_delta: float, job: scheduler.util.AbstractJob, max_exec: int, job_count: int
    ) -> float:
        """Interprete the Job's weight as its priority"""
        _ = max_exec
        _ = job_count
        if time_delta < 0:
            return 0
        return job.weight

Instantiate the :class:`~scheduler.core.Scheduler` with the custom priority function.

.. code-block:: pycon

    >>> import datetime as dt
    >>> from scheduler import Scheduler
    >>> from scheduler.util import Prioritization as Prio

    >>> now = dt.datetime.now()
    >>> sch = Scheduler(max_exec=3, priority_function=Prio.constant_weight_prioritization)

Schedule some :class:`~scheduler.job.Job`\ s at different points in the past with distinct weights:

.. code-block:: pycon

    >>> for delayed_by, weight in ((2, 1), (3, 2), (1, 3), (4, 4)):
    ...     exec_time = now - dt.timedelta(seconds=delayed_by)
    ...     job = sch.once(
    ...         exec_time,
    ...         print,
    ...         params={"end": f"{weight = }; {delayed_by = }s\n"},
    ...         weight=weight,
    ...     )

Note how the columns ``due in`` and ``weight`` in the following table reflect the definitions of
our :class:`~scheduler.job.Job`\ s.

.. code-block:: pycon

    >>> print(sch)  # doctest:+SKIP
    max_exec=3, timezone=None, priority_function=constant_weight_prioritization, #jobs=4
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    ONCE     print(?)         2021-07-02 20:43:47  -0:00:04           0/1      4
    ONCE     print(?)         2021-07-02 20:43:48  -0:00:03           0/1      2
    ONCE     print(?)         2021-07-02 20:43:49  -0:00:02           0/1      1
    ONCE     print(?)         2021-07-02 20:43:50  -0:00:01           0/1      3
    <BLANKLINE>

In contrast to the second the example in :ref:`examples.weights.default_behaviour`
the time delay is not taken into consideration in the execution order of the
:class:`~scheduler.job.Job`\ s.

.. code-block:: pycon

    >>> exec_count = sch.exec_jobs()
    weight = 4; delayed_by = 4s
    weight = 3; delayed_by = 1s
    weight = 2; delayed_by = 3s

Due to the :class:`~scheduler.core.Scheduler`'s limit on the execution count argument
`max_exec`, the :class:`~scheduler.job.Job` with the lowest weight is still residing
in the :class:`~scheduler.core.Scheduler`.

.. code-block:: pycon

    >>> print(sch)  # doctest:+SKIP
    max_exec=3, timezone=None, priority_function=constant_weight_prioritization, #jobs=1
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    ONCE     print(?)         2021-07-02 21:07:17  -0:00:02           0/1      1
    <BLANKLINE>


Uniform Random Prioritization
-----------------------------

This example demonstrates, how the priority function can be used to implement behaviours
resembling more of a load balancer than a classical scheduler.

The following function implementation interpretes the `weight` of a :class:`~scheduler.job.Job`
as a probability for it's execution using the `uniformly distributed`_ random number
generator `random.random()`. With `random.random()` generating values in the interval
``[0,1)``, the :class:`~scheduler.job.Job`'s `weight`\ s of ``0``, ``0.3`` and ``1`` would be interpreted as a probabilities
of ``0%``, ``30%`` and ``100%``.

.. warning:: In contrast to a regular scheduler the following example completely disregards
    the time element.

The :class:`~scheduler.core.Scheduler` expects a prioritization function of the signature
``Callable[[float, Job, int, int], float]``. The custom prioritization function is
available in :mod:`~scheduler.util` as :meth:`~scheduler.util.Prioritization.random_priority_function`.

.. code-block:: python

    import random
    import scheduler

    def random_priority_function(
        time: float, job: scheduler.util.AbstractJob, max_exec: int, job_count: int
    ) -> float:
        """
        Simple uniform random priority generator.

        The priority generator will return 1 if the random number
        is lower then the Job's weight, otherwise it will return 0.
        """
        _ = time
        _ = max_exec
        _ = job_count
        if random.random() < job.weight:
            return 1
        return 0

Now instantiate a :class:`~scheduler.core.Scheduler` with the custom `random_priority_function`. Then create
some generic :class:`~scheduler.job.Job`\ s with probabilities from ``0%`` to ``100%``:

.. code-block:: pycon

    >>> import datetime as dt
    >>> from scheduler import Scheduler
    >>> from scheduler.util import Prioritization as Prio

    >>> sch = Scheduler(priority_function=Prio.random_priority_function)

    >>> jobs = {}
    >>> for percentage in range(0,101,10):
    ...     jobs[percentage] = sch.cyclic(
    ...         dt.timedelta(),
    ...         lambda: None,
    ...         weight=0.01*percentage,
    ...     )

We can verify that the expected number of :class:`~scheduler.job.Job`\ s with the given probabilities are scheduled:

.. code-block:: pycon

    >>> print(sch)  # doctest:+SKIP
    max_exec=inf, timezone=None, priority_function=random_priority_function, #jobs=11
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   <lambda>()       2021-07-02 23:43:38  -0:00:00         0/inf    0.0
    CYCLIC   <lambda>()       2021-07-02 23:43:38  -0:00:00         0/inf    0.1
    CYCLIC   <lambda>()       2021-07-02 23:43:38  -0:00:00         0/inf    0.2
    CYCLIC   <lambda>()       2021-07-02 23:43:38  -0:00:00         0/inf    0.3
    CYCLIC   <lambda>()       2021-07-02 23:43:38  -0:00:00         0/inf    0.4
    CYCLIC   <lambda>()       2021-07-02 23:43:38  -0:00:00         0/inf    0.5
    CYCLIC   <lambda>()       2021-07-02 23:43:38  -0:00:00         0/inf    0.6
    CYCLIC   <lambda>()       2021-07-02 23:43:38  -0:00:00         0/inf 0.700#
    CYCLIC   <lambda>()       2021-07-02 23:43:38  -0:00:00         0/inf    0.8
    CYCLIC   <lambda>()       2021-07-02 23:43:38  -0:00:00         0/inf    0.9
    CYCLIC   <lambda>()       2021-07-02 23:43:38  -0:00:00         0/inf    1.0
    <BLANKLINE>

For the next step we run a small statistical experiment and perform ``10k`` executions
with the :class:`~scheduler.core.Scheduler`.

.. code-block:: pycon

    >>> total_counts = 10_000
    >>> for _ in range(total_counts):
    ...     exec_count = sch.exec_jobs()

Utilizing the `Job.attempts` property we can observe the number of executions. For
direct comparision with the target probabilities we normalize the results by the total counts.
If everything is behaving correctly we would expect the results to approach the target
probabilities with for increasing total counts.

.. code-block:: pycon

    >>> for percentage, job in jobs.items():  # doctest:+SKIP
    ...     print("{:>3} {:>5.1f}".format(percentage, 100*job.attempts/total_counts))
      0   0.0
     10  10.2
     20  19.9
     30  30.1
     40  39.4
     50  49.7
     60  59.3
     70  70.3
     80  79.8
     90  90.5
    100 100.0

The results in this experiment conform to what one would expect for a `uniformly distributed`_
random variable.

.. _uniformly distributed: https://en.wikipedia.org/wiki/Continuous_uniform_distribution