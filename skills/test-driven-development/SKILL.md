---
name: test-driven-development
description: Builds features and bug fixes test-first, writing one failing test, watching it fail for the right reason, then writing the least code that makes it pass. Use when implementing a new feature, function, or behavior change, when fixing a bug, or when about to write production code that has no test yet.
---

# Test-Driven Development

> Adapted from [`test-driven-development`](https://github.com/obra/superpowers/tree/main/skills/test-driven-development) in obra/superpowers by Jesse Vincent (MIT License). Changes: restructured to match this repository's format; the "delete code written first" rule reworded as a set-aside step; testing guidance condensed into `references/writing-good-tests.md`.

## Overview

A test you never saw fail proves nothing. It might test the wrong thing, test a mock instead of the code, or be unable to fail at all. Tests written after the code tend to check what the code already does, not what it should do, and they pass on the first run, so nobody finds out.

Writing the test first fixes that. The test fails because the behavior is missing, you write just enough code to make it pass, and now you know the test can catch a break.

```
NO PRODUCTION CODE WITHOUT A TEST THAT FAILED FIRST
```

## When to Use

- Adding a feature, function, endpoint, or calculation
- Fixing a bug (the failing test is the bug's reproduction)
- Changing existing behavior, such as a new rule, limit, or format
- Any time you're about to write code that has no test covering it

**When NOT to use:** throwaway prototypes and exploration spikes (throw them away before building the real thing), generated code, and pure configuration. Check with the user before treating anything else as an exception. For changing the structure of code without changing its behavior, use `safe-refactoring`, which pins existing behavior first.

## The Process

### Step 1: Write one failing test

Pick the next smallest behavior and write one test for it. Name it after the behavior ("charges a late fee after 30 days"), not the function ("test calculate"). Use the real code, with mocks only for things that are slow or external. Before writing the assertion, name the code change that should make this test fail; if you can't, the test isn't checking anything. See `references/writing-good-tests.md`.

### Step 2: Watch it fail for the right reason

Run the test. It should **fail**, not error, and the failure message should say the behavior is missing (expected 25.00, got 0). If it errors on an import or a typo, fix that and run again. If it **passes**, either the behavior already exists or the test can't fail; fix the test before going on.

### Step 3: Write the least code that passes

Write the simplest code that makes this test pass. No extra options, no handling for cases no test asks for yet, no cleanup of nearby code. Hard-coding is fine if it's what the test demands; the next test will force the real logic.

### Step 4: Watch it pass, and run everything

Run the test (it should pass), then run the project's full test command, not just your file. A green single test is not a green suite. If something else fails, fix it now or, if it was already failing before you started, name it in your report.

### Step 5: Clean up while green

Now improve names, remove duplication, and extract helpers. Run the tests after each change. Don't add behavior here; new behavior starts back at Step 1.

### Step 6: Repeat

Pick the next behavior and go back to Step 1. Cover the edge cases that matter for this code: empty input, zero, boundaries, invalid data, and error paths.

### If you already wrote code before the test

Move it aside (for example, `git stash`), write the test, and confirm it fails without the code. Then build the implementation back up to what the test requires, rather than pasting the old version back in whole. Otherwise you're back to testing after.

### Bugs

Write a test that reproduces the bug and fails, then fix. The test proves the fix and stops the bug from coming back. To find the cause first, use `systematic-debugging` if installed.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It's too simple to test." | Simple code breaks too, and the test takes a minute. |
| "I'll write the tests after." | Tests written after pass immediately, which proves nothing. |
| "I already tested it by hand." | Manual checks leave no record and can't be re-run after the next change. |
| "I've spent hours on this code, I'm not throwing it away." | Set it aside, write the test, and rebuild. Code you can't verify isn't saving time. |
| "This is hard to test." | Hard to test usually means hard to use. Simplify the interface. |
| "I need to mock everything." | The code is too tangled. Pass dependencies in instead of reaching for them. |
| "The existing code has no tests." | Add tests for the part you're changing, starting now. |

## Red Flags

- Production code written before any test for it
- A new test that passes on its first run
- Not being able to say why a test failed
- Assertions that check a mock was called rather than what the code produced
- An expected value computed by the same code under test
- Running only the one test file before calling it done
- "Tests later", "just this once", "it's different because..."

## Verification

- [ ] Each new behavior has a test that was seen failing for the expected reason
- [ ] The code written was the least needed to pass
- [ ] The full test suite was run fresh after the last change
- [ ] Edge cases and error paths that matter are covered
- [ ] Tests use real code, with mocks only for slow or external parts
- [ ] Output is clean (no new errors or warnings), as `verification-before-completion` describes
