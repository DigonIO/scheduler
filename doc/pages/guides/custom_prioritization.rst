Custom Prioritization
=====================

In one of the examples we already discussed, how the default implementation of the
:class:`~scheduler.job.Job` `prioritization` works.
A short recap, the time in seconds a `Job` is overdue is multiplied by the `Job`\ 's `weight`,
which leads to a linear `priority_function`.
If the `prioritization` value is smaller or equal to zero, the `Job` is dismissed.

Depending on the application an alternative `priority_function` is required.
Similar to the linear `prioritization` a quadratic or exponential model can be used.
Besides these well known relations abstract `priority_function`\ s can be implemented.

Let's define our own custom `priority_function`\ s and learn how to apply it to the 
:class:`~scheduler.scheduler.Scheduler`.
We have two tasks where we decouple the `prioritization` from overdue time
to demonstrate how versatile a custom `priority_function` is.

Pure Weight Prioritization
--------------------------

In this first task we define a `pure weight prioritization`,
which means that the `priority_function` directly passes the `weight` of the `Job` as a return value.
This is especially interesting if the number of `Job`\ s to be executed when calling
:func:`~scheduler.scheduler.Scheduler.exec_jobs` is limited at the same time.

We start the implementation with all required imports
and then custom `priority_function`.

.. code-block:: pycon

    >>> import datetime as dt
    >>> import scheduler

    >>> def pure_weight_prioritization(
    ... seconds: float, job: scheduler.util.AbstractJob, max_exec: int, job_count: int
    ... ) -> float:
    ...     """Return the weight of the `Job` as priorization value."""
    ...     _ = seconds
    ...     _ = max_exec
    ...     _ = job_count
    ...     return job.weight

We also define a function that allows the `Job` to indicate what weight it has.

    >>> def print_weight(job_name: str):
    ...     """Simple print statement as `Job` payload."""
    ...     print(job_name)

Now we can instantiate the :class:`~scheduler.scheduler.Scheduler`,
we pass the custom `priority_function` and the limit on the number
of executable `Job`\ s with ``1``.
Then we verify the `Scheduler` by a simple `print(sch)` statement.

.. code-block:: pycon

    >>> sch = scheduler.Scheduler(priority_function=pure_weight_prioritization, max_exec=1)
    >>> print(sch)
    max_exec=1, timezone=None, priority_function=pure_weight_prioritization, #jobs=0
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    <BLANKLINE>

In the next step, we schedule a cyclic a `Job` with a `weight` of ``1`` that will be executed ``2`` times.
By executing a `print(sch)` statement, we can see the scheduled `Job` in the table.

.. code-block:: pycon

    >>> j_1 = sch.cyclic(
    ...         dt.timedelta(),
    ...         print_weight,
    ...         params={"job_name": "j_1"},
    ...         weight=1,
    ...         max_attempts=2,
    ...     )
    >>> print(sch)  # doctest:+SKIP
    max_exec=1, timezone=None, priority_function=pure_weight_prioritization, #jobs=1
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   print_weight(..) 2021-07-01 18:51:23  -0:00:00           0/2      1
    <BLANKLINE>

Calling the function :func:`~scheduler.scheduler.Scheduler.exec_jobs` executes the job once.
We can see the output ``j_1`` of the `print_weight` function defined above.
In the table we can also see that the `Job` was executed once.

.. code-block:: pycon

    >>> exec_count = sch.exec_jobs()
    j_1
    >>> print(sch)  # doctest:+SKIP
    max_exec=1, timezone=None, priority_function=pure_weight_prioritization, #jobs=1
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   print_weight(..) 2021-07-01 18:53:09  -0:00:00           1/2      1
    <BLANKLINE>

To make the weights relevant for the first time, we bring a second `Job` into play
that has twice the `weight` of the first one.

.. code-block:: pycon

    >>> j_2 = sch.cyclic(
    ...     dt.timedelta(),
    ...     print_weight,
    ...     params={"job_name": "j_2"},
    ...     weight=2,
    ...     max_attempts=2,
    ... )
    >>> print(sch)  # doctest:+SKIP
    max_exec=1, timezone=None, priority_function=pure_weight_prioritization, #jobs=2
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   print_weight(..) 2021-07-01 18:53:31  -0:00:00           1/2      1
    CYCLIC   print_weight(..) 2021-07-01 18:53:31  -0:00:00           0/2      2
    <BLANKLINE>

We now expect that the output by calling the :func:`~scheduler.scheduler.Scheduler.exec_jobs`
function no longer outputs ``j_1`` but ``j_2``, which is also confirmed.
Both `Job`\ s can now be executed only one more time.

.. code-block:: pycon

    >>> exec_count = sch.exec_jobs()
    j_2
    >>> print(sch)  # doctest:+SKIP
    max_exec=1, timezone=None, priority_function=pure_weight_prioritization, #jobs=2
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   print_weight(..) 2021-07-01 18:54:24  -0:00:00           1/2      1
    CYCLIC   print_weight(..) 2021-07-01 18:54:24  -0:00:00           1/2      2
    <BLANKLINE>


A last `Job` is introduced with a `weight` of ``3``, but this one can be executed only once.

.. code-block:: pycon

    >>> j_3 = sch.cyclic(
    ...     dt.timedelta(),
    ...     print_weight,
    ...     params={"job_name": "j_3"},
    ...     weight=3,
    ...     max_attempts=1,
    ... )
    >>> print(sch)  # doctest:+SKIP
    max_exec=1, timezone=None, priority_function=pure_weight_prioritization, #jobs=3
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   print_weight(..) 2021-07-01 18:55:00  -0:00:00           1/2      1
    CYCLIC   print_weight(..) 2021-07-01 18:55:00  -0:00:00           1/2      2
    ONCE     print_weight(..) 2021-07-01 18:55:00  -0:00:00           0/1      3
    <BLANKLINE>

Calling the :func:`~scheduler.scheduler.Scheduler.exec_jobs` function again
outputs ``j_3`` according to the known scheme.
If you look at the table you will notice that the executed `Job` is no longer visible,
the `Scheduler` has removed it because it had no more open attempts.

.. code-block:: pycon

    >>> exec_count = sch.exec_jobs()
    j_3
    >>> print(sch)  # doctest:+SKIP
    max_exec=1, timezone=None, priority_function=pure_weight_prioritization, #jobs=2
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   print_weight(..) 2021-07-01 18:56:13  -0:00:00           1/2      1
    CYCLIC   print_weight(..) 2021-07-01 18:56:13  -0:00:00           1/2      2

To finish the remaining two `Job`\ s, the :func:`~scheduler.scheduler.Scheduler.exec_jobs` function is called twice. 
We can again see their output ``j_2`` and ``j_1`` in the correct order due to the weighting.
The table is now empty, since no more `Job`\ s are scheduled.

.. code-block:: pycon

    >>> exec_count = sch.exec_jobs()
    j_2
    >>> exec_count = sch.exec_jobs()
    j_1
    >>> print(sch)
    max_exec=1, timezone=None, priority_function=pure_weight_prioritization, #jobs=0
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    <BLANKLINE>


Uniform Random Prioritization
-----------------------------

The goal of this second task is to modify  the class:`~scheduler.core.Scheduler` to random generator,
which executes :class:`~scheduler.job.Job`\ s using a `uniform distributed`_ random variable.
So a classical scheduling is not wanted here either, instead a `Job` is given a probability
of ``0%`` to ``100%`` via its `weight`.

To make this possible we need to implement an alternative for the default `priority_function`.
This custom function, let's call it `random_priority_function`, is used when instantiating the `Scheduler`
by passing it to the `priority_function` argument.

After the necessary imports we define our custom `random_priority_function`.
We make sure that the signature of the function is the same as the signature of the default implementation.
The core of the function is the comparison of the `weight` of the `Job` with a uniformly distributed
random number between ``[0,1)``.
If the random number is smaller than the `weight`, the function returns ``1`` and the `job` is executed,
else the random number is greater than the `weight`, ``0`` is returned and the `Job` is not executed.
The time a `Job` is overdue and other metrics are ignored.

.. code-block:: pycon

    >>> import datetime as dt
    >>> import random
    >>> from scheduler import Scheduler

    >>> def random_priority_function(
    ...     seconds: float, job: scheduler.util.AbstractJob, max_exec: int, job_count: int
    ... ) -> float:
    ...     """
    ...     Simple uniform random priority generator.
    ...
    ...     The priority generator will return 1 if the random number
    ...     is lower then the `Job` weight, else it will return 0.
    ...     The value 0 means that a `Job` won't be executed.
    ...     """
    ...     _ = seconds
    ...     _ = max_exec
    ...     _ = job_count
    ...
    ...     if random.random() < job.weight:
    ...         return 1
    ...     return 0

To measure if the `Scheduler` keeps the probabilities defined by the `weights` of the `Job`\ s
we uise a function which increments a counter for each execution.
The reference of the function, and the references to the parameters are passed to the `Job`\ s when they are
instancation.

    >>> def probability_exec_counter(probabilities: dict[float, int], probability: float):
    ...     """Bump the execution count for a given probability."""
    ...     probabilities[probability] += 1

Now we instantiate our `Scheduler` and pass it our custom `random_priority_function`.
With a `print(sch)` statement we can verify that the `Scheduler` does not use the default `priority_function`.

.. code-block:: pycon

    >>> sch = scheduler.Scheduler(priority_function=random_priority_function)
    >>> print(sch)
    max_exec=inf, timezone=None, priority_function=random_priority_function, #jobs=0
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    <BLANKLINE>

We verify the functionality of the `uniform random prioritization` with the help of a small experiment.
For this we determine ``11`` measuring points ``{0.0, 0.1, ... 1.0}`` which represent the probability
from ``0%`` to ``100%``. We store these probabilities in the `probabilities dict`,
where a probability maps to a number of executions.

    >>> probabilities: dict[float, int] = {0.1 * idx: 0 for idx in range(0,11)}

Since no classical scheduling is used, we create `Job` using the function 
:func:`~scheduler.scheduler.Scheduler.cyclic` and simply pass an empty
`datetime.timedelta` object.
We create a `Job` for each probability to be measured and pass the references
to the function `probability_exec_counter` and the corresponding arguments.

    >>> for probability in probabilities:
    ...     job = sch.cyclic(
    ...         dt.timedelta(),
    ...         probability_exec_counter,
    ...         params={"probabilities": probabilities, "probability": probability},
    ...         weight=probability,
    ...     )

After creating the `Job`\ s we verify the `Scheduler` again by a simple
`print(sch)` statement. The `Job`\ s are displayed in the table. If you pay attention to the
`weights`, the desired probabilities can be found.

.. code-block:: pycon

    >>> print(sch)  # doctest:+SKIP
    max_exec=inf, timezone=None, priority_function=random_priority_function, #jobs=11
    <BLANKLINE>
    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   #xec_counter(..) 2021-07-01 18:59:48  -0:00:00         0/inf    0.0
    CYCLIC   #xec_counter(..) 2021-07-01 18:59:48  -0:00:00         0/inf    0.1
    CYCLIC   #xec_counter(..) 2021-07-01 18:59:48  -0:00:00         0/inf    0.2
    CYCLIC   #xec_counter(..) 2021-07-01 18:59:48  -0:00:00         0/inf 0.300#
    CYCLIC   #xec_counter(..) 2021-07-01 18:59:48  -0:00:00         0/inf    0.4
    CYCLIC   #xec_counter(..) 2021-07-01 18:59:48  -0:00:00         0/inf    0.5
    CYCLIC   #xec_counter(..) 2021-07-01 18:59:48  -0:00:00         0/inf 0.600#
    CYCLIC   #xec_counter(..) 2021-07-01 18:59:48  -0:00:00         0/inf 0.700#
    CYCLIC   #xec_counter(..) 2021-07-01 18:59:48  -0:00:00         0/inf    0.8
    CYCLIC   #xec_counter(..) 2021-07-01 18:59:48  -0:00:00         0/inf    0.9
    CYCLIC   #xec_counter(..) 2021-07-01 18:59:48  -0:00:00         0/inf    1.0
    <BLANKLINE>

We have now completed all preparations to execute the 'Job'\ s according to their probability.
To check whether the probabilities are correct we need a little bit of statistics,
so we perform ``10k`` execution attempts.
Note that no time intervals are needed between the executions,
because the selection of the ``Job`` s is purely random and do not depend on the time.

    >>> max_counts = 10000
    >>> for _ in range(max_counts):  # doctest:+SKIP
    ...     sch.exec_jobs()
    4
    6
    5
    ...

Finally, we evaluate the data stored in the `probability dict`.
Thereby we consider the normalization to the number of execution attempts.
According to the result of our experiment, the `Scheduler` modified as a random generator
works correctly as defined according to a `uniform distribution`_.

    >>> print("Desired probability ; measured probability")
    Desired probability ; measured probability
    >>> for probability, count in probabilities.items():
    ...     print(probability,";", count/max_counts)
    0.0 ; 0.0
    0.1 ; 0.0972
    0.2 ; 0.1999
    0.3 ; 0.2972
    0.4 ; 0.4042
    0.5 ; 0.4921
    0.6 ; 0.6032
    0.7 ; 0.6972
    0.8 ; 0.8047
    0.9 ; 0.8988
    1.0 ; 1.0

.. _uniform distribution: https://en.wikipedia.org/wiki/Continuous_uniform_distribution
.. _uniform distributed: https://en.wikipedia.org/wiki/Continuous_uniform_distribution