# Flaky Failures

Load this when a failure happens only sometimes: in CI but not locally, under load, when tests run together, or seemingly at random.

## Treat "sometimes" as information

An intermittent failure still has a cause. It usually falls into one of a few groups:

| Pattern | Likely cause | How to check |
|---|---|---|
| Fails in CI, passes locally | Different environment: versions, env vars, time zone, file paths, missing secrets | Print versions and key env vars in both places and compare |
| Fails only when the full suite runs | Shared state between tests: a global, a file, a database row, a cached value | Run the failing test alone, then with each other file before it |
| Fails more on slow machines | Timing: the code checks a result before it's ready | Look for fixed sleeps and waits; add a delay to make it fail every time |
| Fails on certain days or times | Dates and time zones: month ends, daylight saving changes, "today" | Freeze or set the clock in the test and try the edge dates |
| Fails with certain data | An input the code doesn't handle: empty, very long, special characters, duplicates | Log the input on failure and retry with that exact input |

Try to make it fail every time. Once it's reliable, debug it like any other bug.

## Replace guessed waits with condition waits

A common cause is a fixed delay that guesses how long something takes:

```
wait 0.5 seconds
check the result        # passes on a fast machine, fails on a busy one
```

Wait for the actual condition instead, with a timeout and a clear message:

```
repeat every ~10 ms, for up to 5 seconds:
    if the result exists: stop waiting
if it never appeared: fail with "timed out waiting for <what>"
```

Check the condition fresh inside the loop rather than reading a value saved before it. Most test frameworks already provide this (for example, Playwright's auto-waiting locators, `waitFor` in Testing Library, or polling helpers in pytest plugins); prefer those over writing your own.

A fixed delay is right only when the timing itself is what you're testing, such as a debounce or a rate limit. Then wait for the triggering condition first, base the delay on the known interval, and comment why that number was chosen.
