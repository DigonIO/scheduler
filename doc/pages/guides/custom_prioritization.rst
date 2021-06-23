Custom Prioritization
=====================

foo

Pure Weight Prioritization
--------------------------

foo

Unifrom Random Prioritization
-----------------------------

.. code-block:: pycon

    >>> import datetime as dt
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
    
    >>> def probability_exec_counter(probabilities: dict[float, int], probability: float):
    ...     """Bump the execution count for a given probability."""
    ...     probabilities[probability] += 1

    >>> sch = scheduler.Scheduler(priority_function=random_priority_function)
    >>> print(sch)
    max_exec=inf, timezone=None, priority_function=random_priority_function, #jobs=0

    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------

    >>> probabilities = {0.1 * idx: 0 for idx in range(0,11)}

    >>> for probability in probabilities:
    ... sch.cyclic(
    ...     dt.timedelta(),
    ...     probability_exec_counter,
    ...     params={"probabilities": probabilities, "probability": probability},
    ...     weight=probability,
    ... )

    >>> print(sch)
    max_exec=inf, timezone=None, priority_function=random_priority_function, #jobs=11

    type     function         due at                 due in      attempts weight
    -------- ---------------- ------------------- --------- ------------- ------
    CYCLIC   #ity_counter(..) 2021-06-22 18:52:15    -1 day         0/inf    0.0
    CYCLIC   #ity_counter(..) 2021-06-22 18:52:15    -1 day         0/inf    0.1
    CYCLIC   #ity_counter(..) 2021-06-22 18:52:15    -1 day         0/inf    0.2
    CYCLIC   #ity_counter(..) 2021-06-22 18:52:15    -1 day         0/inf 0.300#
    CYCLIC   #ity_counter(..) 2021-06-22 18:52:15    -1 day         0/inf    0.4
    CYCLIC   #ity_counter(..) 2021-06-22 18:52:15    -1 day         0/inf    0.5
    CYCLIC   #ity_counter(..) 2021-06-22 18:52:15    -1 day         0/inf 0.600#
    CYCLIC   #ity_counter(..) 2021-06-22 18:52:15    -1 day         0/inf 0.700#
    CYCLIC   #ity_counter(..) 2021-06-22 18:52:15    -1 day         0/inf    0.8
    CYCLIC   #ity_counter(..) 2021-06-22 18:52:15    -1 day         0/inf    0.9
    CYCLIC   #ity_counter(..) 2021-06-22 18:52:15    -1 day         0/inf    1.0

    >>> max_counts = 10000
    >>> for _ in range(max_counts):
    ...     sch.exec_jobs()

    >>> print("Desired probability ; measured probability")
    >>> for probability, count in probabilities.items():
    ...     print(probability,";", count/max_counts)
    Desired probability ; measured probability
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
