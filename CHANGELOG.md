# Changelog

## 0.8.8

### Misc

+ Type hint Scheduler.once() `args` as a variadic generic tuple
  (Thanks [@sanurielf](https://github.com/sanurielf)),
  [PR #9](https://github.com/DigonIO/scheduler/pull/9)
+ Python 3.13 support.

## 0.8.7

+ Version bump to fix CI/CD process

## 0.8.6

### Bugfix

+ Fixed misue of `tags` argument (was dict where it should have been set)
  and allowed to pass as `Iterable`.

### Misc

+ Fix a number of type annotations
  + `BaseScheduler` is now generic
  + `BaseJob` is now generic
  + Fixed annotations for Coroutines in asyncio scheduler
  + Disable mypy's strict mode for now (ignores `**kwargs` typing for now)
+ Added type annotations into testing code
+ Migrate from `setup.py` to `pyproject.toml`

## 0.8.5

### Misc

+ Python 3.12 support.
+ [Issue#18](https://gitlab.com/DigonIO/scheduler/-/issues/18) fixed
  (Thanks [@bshakur8 (Bhaa Shakur)](https://github.com/bshakur8),
  [PR #7](https://github.com/DigonIO/scheduler/pull/7))
+ Improved deprecation warnings
  (Thanks [@bshakur8 (Bhaa Shakur)](https://github.com/bshakur8),
  [PR #6](https://github.com/DigonIO/scheduler/pull/6))

## 0.8.4

### Bugfix

+ [Issues#16](https://gitlab.com/DigonIO/scheduler/-/issues/16#note_1316075776) `Typeguard` API
  migration.

## 0.8.3

### Misc

+ Migrate from [ReadTheDocs](https://readthedocs.org/) to [HostYourDocs](https://github.com/DigonIO/hostyourdocs).
+ Custom docs colour theme.

## 0.8.2

### Misc

+ Add `CONTRIBUTING.md`.
+ Include `pre-commit` config.

### Bugfix

+ Fix deadlock bug [Issue#15](https://gitlab.com/DigonIO/scheduler/-/issues/15).
+ Fix displaying of DeprecationWarning for the `delay` flag.

## 0.8.1

### Misc

+ Python 3.11 support.

### Testing

+ The library is now also tested against python version 3.11.
+ Update patches for other python versions.

## 0.8.0

### Features

+ Catching unhandled exceptions of scheduled functions
  ([Issue#13](https://gitlab.com/DigonIO/scheduler/-/issues/13)):
  + Introduced logging for unhandled exceptions.
  + The scheduler takes a custom logger instance as argument.
  + Jobs are now counting the number of unhandled exceptions.

### Misc

+ Improved some exception messages.
+ Minor documentation corrections.
+ Minor README.md corrections and simplifications.
+ Removed deprecated Prioritization code from `util.py`.

### Bugfix

+ Some exception messages that previously were wrongly tested and therefore ignored.
  are now matched using the `match` argument in `pytest.raises`.
+ Bugfix in PKGBUILD's package() function.

## 0.7.4

### Misc

+ formatting of README.md
+ CI file correction for coverage report

## 0.7.3

### Testing

+ `test_readme.py` now uses monkeypatched `datetime.now()`
+ Tests are contained in their own modules therefore installation before testing
  is no longer necessary
+ testing requirements now include `typeguard`
+ coverage badge should work again

### Misc

+ sponsor Digon.IO added

## 0.7.2

### Features

+ aliases are now supported for Scheduler.once

### Misc

+ Skipping checksum in PKGBUILD (we do not know the hash in advance of pushing)
+ Added missing checkdepends: `python-pytest-asyncio`

### Documentation

+ String fixes: `function / alias` and spaces
+ additional alias example
+ corrected alias_text
+ tag & parameters - remove unneeded `doctest:+ELLIPSIS` instruction
+ note added on tags

## 0.7.1

### Misc

+ Bump version in PKGBUILD.
+ Fix image for release stage.

## 0.7.0

### Features

+ Added a scheduler for asyncio under the import path `scheduler.asyncio.Scheduler`.

### Bugfixes

+ The deletion of an unscheduled `Job` with the `scheduler.Scheduler.delete_job` method raised
  a `KeyError`. This was corrected and it will now raise a `SchedulerError`.

### Misc

+ Refactoring of the internal code structure.
+ New namespace conventions.
+ Revision of the `setup.py` file.
+ Revision of the README.md.
+ Documentation updated.
+ The documentation now uses the [furo](https://github.com/pradyunsg/furo) theme.

### Deprecation warnings

+ The `delay` argument used when scheduling jobs of different types will be removed
  in a future release.

### Known issues

+ Some mypy errors arise due to implementation details regarding the inheritance of the `BaseJob`
  and `BaseScheduler`.

## 0.6.3

### Bugfixes

+ Fix the missing lock acquiring in the `JobTimer` described as bug in the
  [issue #10](https://gitlab.com/DigonIO/scheduler/-/issues/10).

### Misc

+ Fix the version of `mistune` in the `requirement.txt` to prevent pipeline failure
  (`m2r2` dependency, not fixed there).

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
