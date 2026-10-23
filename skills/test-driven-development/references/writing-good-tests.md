# Writing Good Tests

Load this when writing or changing tests, adding mocks, or adding test helpers.

A test exists to catch a specific break. Two rules cover most of what goes wrong:

1. Every test names the break it catches.
2. Every test exercises the real code.

## Name the break

Before writing the test body, answer: what change to the production code should make this test fail, and is that change a bug or a deliberate decision?

**Derive expected values by hand.** Use literals and hand-checked examples. An expected value computed by the code under test (or its helpers) matches no matter what the code does:

```
# Always passes: both sides come from the same function
expected = build_invoice_number(2026, 41)
assert build_invoice_number(2026, 41) == expected

# Catches a real break
assert build_invoice_number(2026, 41) == "INV-2026-0041"
```

Table-driven tests with literal expected values are a good default shape.

**Test behavior, not decisions.** A test that only fails when someone intentionally changes a constant, a message's wording, or private structure fires on every redesign and never on a bug. Instead of asserting `MAX_RETRIES == 5`, assert that a failing call is tried five times and the sixth attempt never happens.

**Run things, don't read them.** Checking that a script or config file contains an exact line proves only that the file is the file. Run the script against a controlled input and check its output, side effects, or exit code.

**Test your code, not the framework.** Test the contract at your boundaries: the route you register, the query you build, the payload you send. Don't test that the framework calls a handler; that's its maintainers' job. Plain getters, constants, and pass-through functions don't need their own tests; test the first result someone would actually see that depends on them.

## Exercise the real code

**Never assert on a mock.** An assertion that a mock was rendered or called passes when the mock exists and says nothing about your code. Assert the real result instead, or remove the mock.

**Mock at the right level.** Before replacing a method, learn everything it does. Mock only the slow or external part (the network call, the email send) and keep the parts your test depends on real. If you're unsure, run the test against the real thing first and watch what it needs.

**Make fakes specific.** When arguments, call counts, or order are part of the contract, assert them. Give success, error, and malformed responses separate fixtures, so the wrong branch can't satisfy the test.

**Mirror real data completely.** A fake API response should have every field the real one has, not just the fields this test reads. Partial fakes pass while the real integration breaks on a field nobody included.

**Keep test-only code out of production.** Cleanup or reset methods that only tests call belong in test helpers, not on production classes.

**Prefer real components over elaborate mocks.** When mock setup is longer than the test itself, or tests break every time a mock changes, switch to a test with real components.

## The mutation check

Before finishing, imagine small mistakes in the production code. For each realistic one, at least one test should fail:

- A wrong constant or argument
- The wrong branch taken
- A missing state change or side effect
- An empty or default return value
- Missing validation for zero, empty, missing, unauthorized, or malformed input

A mistake no test would catch marks behavior that isn't protected, or a test that can't fail.

## Warning signs

- Setup and assertion use the same object, so they're guaranteed to match
- The test can only fail by crashing
- The test fails on every intentional change and never on accidental ones
- Expected values are hidden in loops, builders, or helpers
- The test reads source text instead of running anything
- An assertion would fail if you removed the mock, and pass otherwise
- A method is only ever called from test files
- Mock setup is more than half the test, or nobody can say why the mock is there
