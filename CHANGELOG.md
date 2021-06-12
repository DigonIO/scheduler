# Changelog

## 0.4.0

### Features

+ Delete all scheduled `Job`s using a single command.
+ Added `__repr__` and `__str__` methods to `Job`
+ Execute all scheduled `Job`s regardless of when they are scheduled.
+ `Job`s can be passed to `Scheduler.__init__`
+ `Job` exposes property `tzinfo`

### API changes

+ `Job.has_attempts` is now `Job._has_attempts_remaining` as it has no meaningful use for the end user.
+ `Scheduler._add_job` removed

### Misc

+ Improved examples and docs.

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
