# Python review checklist

Prompts for where Python bugs hide. Each item is a place to look, not something to
report on sight: report only what you can show is wrong in this code.

## Correctness

- Mutable default arguments; class attributes shared across instances by accident.
- Truthiness checks that mishandle `0`, `""`, empty collections, or `None` (`if x:`
  where `if x is not None:` was meant).
- Late-binding closures in loops and comprehensions; shadowed builtins and names.
- Mutating a collection while iterating over it; aliasing where a copy was intended.
- Naive vs aware `datetime` mixing, local time where UTC is needed, DST arithmetic.
- `float` for money or exact quantities; integer division and rounding surprises.
- Encoding: missing `encoding=` on `open`, bytes/str confusion, newline handling.
- `is` used for value comparison; `__eq__` without `__hash__`; dataclass ordering and
  mutability.
- Off-by-one errors in slicing, pagination, ranges, and boundary conditions.

## Errors and resources

- Bare `except:` or `except Exception` that swallows errors, hides
  `KeyboardInterrupt`/`CancelledError`, or loses the traceback (`raise X` without
  `from`).
- Files, sockets, DB connections, locks, and subprocesses not closed on every path
  (missing `with`, cleanup only on success).
- Retries without backoff or limits; timeouts missing on network and subprocess calls.
- Errors returned as `None` or sentinel values that callers do not check.

## Concurrency and async

- Blocking I/O or CPU work inside `async def` (`requests`, `time.sleep`, sync DB
  drivers, file I/O on hot paths).
- Fire-and-forget tasks whose exceptions vanish; un-awaited coroutines; tasks not
  cancelled on shutdown.
- Shared mutable state across threads or tasks without locks; check-then-act races
  (including on the filesystem).
- Thread pools or process pools created per call; fork safety with open connections.

## Security

- `subprocess` with `shell=True` or untrusted arguments; `eval`/`exec`.
- SQL built with string formatting; template injection; unsafe `pickle`, `yaml.load`,
  `marshal`.
- Path traversal when joining user input to paths; unsafe archive extraction.
- Secrets in code, logs, exceptions, or default config; disabled TLS verification.
- Missing authorization checks on handlers; trusting client-provided identity or IDs.

## Performance

- N+1 queries; queries or I/O inside loops; loading whole datasets into memory.
- Quadratic algorithms on collections that grow (list membership tests, repeated string
  concatenation).
- Unbounded caches, queues, and buffers; `functools.cache` on methods (keeps instances
  alive).
- Recompiling regexes, re-reading config, or re-creating clients on every call.

## Design and maintainability

- Import cycles and dependency direction that contradicts the layering.
- God modules or classes; functions doing several unrelated things; deep inheritance
  where composition fits.
- Module-level side effects at import time (network, file I/O, global configuration).
- Duplicated logic that has already drifted apart.
- Abstractions with one implementation and one caller; wrappers that only forward.
- Public API without type hints, or `Any` leaking through key interfaces.

## Tests

- Critical paths and error paths with no test (check the coverage report).
- Assertions that cannot fail, or that only check that no exception was raised.
- Tests that depend on order, wall-clock time, network, or shared global state.
- Mocks so broad that the test no longer exercises real behavior.
