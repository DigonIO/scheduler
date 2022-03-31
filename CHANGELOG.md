# Changelog

## 0.7.0

### Deprecation warnings

The `delay` argument used when scheduling jobs of different types will be removed
in the 0.8.0 release.

## 0.6.3

### Bugfixes

+ Fix the missing lock acquiring in the `JobTimer` described as bug in the [issue #10](https://gitlab.com/DigonIO/scheduler/-/issues/10).

### Misc

+ Fix the version of `mistune` in the `requirement.txt` to prevent pipeline failure  (`m2r2` dependency, not fixed there).

## 0.6.2

### API changes

+ `Scheduler` instanciation and `Scheduler.once` arguments are now keyword only.

### Features

+ `Job`s can be given a string alias for identification instead of defaulting to function name.

### Misc

+ Python version requirements added to `setup.py`

## 0.6.1

### Misc

+ Revision of the README.md for the first release on PyPI.org

## 0.6.0

### Features

+ `Job`s can be tagged and filtered by sets of string identifiers

### API changes

+ `Job`: `params` renamed to `kwargs` and introduced `args` keyword analog to
  `sched` library
+ `delete_all_jobs` replaced and implemented within `delete_jobs`
+ `Weekday` implemented as abstract class in `scheduler.trigger.core` instead of
  `Enum` in `scheduler.util`. Now with `time` attribute.
+ `Scheduler.once` and `Scheduler.weekly` no longer accept a tuple of `Weekday, datetime.time`
  for the timing argument.

### Misc

+ `Job` refactoring
+ Documentation updated

## 0.5.2

### API changes

+ Extended `Job` API by `params`, `skip_missing` and `delay`.

### Misc

+ Refactoring of `scheduling` functions using `**kwargs`
+ General documentation improvements

## 0.5.1

### Features

+ Threading support, `scheduler` is now thread safe.
+ Added `n_threads` argument to `Scheduler` for parallel `Job` execution.

### Misc

+ Improved examples and docs.

## 0.5.0

### API changes

+ `Job` batching limited to distinct timings
+ `Job` batching limited to `minutely()`, `hourly()`, `daily()` and `weekly()`

### Bugfixes

+ Behaviour of `skip_missing` adjusted

### Misc

+ Improved documentation (mostly formatting)

## 0.4.0

+ Switched to LGPLv3 License

### Features

+ Delete all scheduled `Job`s using a single command.
+ Added `__repr__` and `__str__` methods to `Job` and `Scheduler`
+ Execute all scheduled `Job`s regardless of when they are scheduled.
+ Added optional `Job` flag: Discard missed executions befor the last pending execution
+ `Job`s can be passed to `Scheduler.__init__`
+ `Job` exposes property `tzinfo`
+ `Job`s support a `start` and `stop` datetime
+ Improved Exception handling
+ Extensive documentation rework

### API changes

+ Completely overhauled `Scheduler` API

### Bugfixes

+ Fixed infinite recursion in `JobTimer` of `calc_next_exec`

### Misc

+ Improved examples and docs.
+ Added Guides and FAQ

## 0.3.0

### Features

+ Allowed parameters to be passed to the function handled by `Job`

### Misc

+ Improved examples and docs
+ Full test coverage :)

## 0.2.0

### API changes

+ Switched `Scheduler` arguments `max_exec` and `tzinfo`.

### Features

+ A `weight_function` can be passed to Scheduler for customizable `Job` weighting.

### Misc

+ Added a changelog
+ Revision of `setup.py`
+ Fixed readthedocs configuration
+ Small optimizations in `README.md` and docs
+ `README.md` embedded within sphinx documentation.
+ Provide a `secrets.py` to support local PyPI caching
+ Improved test coverage

## 0.1.0

+ Initial beta release
