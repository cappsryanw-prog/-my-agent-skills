---
name: safe-refactoring
description: Restructures existing code without changing what it does, using characterization tests and small verified steps. Use when asked to refactor, clean up, simplify, rename, extract, split a large file or function, remove duplication, or "make this code nicer", and whenever a change is meant to be behavior-preserving.
---

# Safe Refactoring

## Overview

A refactor has one promise: the code does exactly what it did before, it is just easier to work with. Most refactors that go wrong break that promise quietly. A default argument changes, an exception type shifts, an import side effect disappears, a sort becomes unstable. Nobody notices until production.

This skill keeps the promise checkable. You pin current behavior with tests first, then move in steps small enough that any break is obvious, and you never mix restructuring with behavior changes.

## When to Use

- The user asks to refactor, clean up, simplify, rename, extract, inline, split, or deduplicate code
- You are about to restructure code as a step toward a feature ("first I'll pull this into a function")
- A file or function has grown too large to change safely

**When NOT to use:**

- The change is meant to alter behavior. That is a feature or a fix: do it as one, and refactor separately before or after.
- Throwaway or prototype code the user has said won't be kept
- A pure formatting pass done by the project's own formatter

## The Process

### Step 1: Define the boundary

State in one sentence what is being restructured and what is **not** changing: the public functions, CLI flags, HTTP routes, file formats, log lines other systems parse, and error types callers catch. Everything that crosses the boundary must behave identically afterward.

Find every caller before you start. Search for the symbol name, string references (reflection, config files, templates, routes), and re-exports. A rename that misses a dynamic reference is a production bug.

### Step 2: Pin current behavior

Run the existing tests for the area and record the result. If coverage is thin, write **characterization tests**: tests that assert what the code does *now*, including odd behavior, not what it should do.

- Cover the normal path, empty and boundary inputs, error paths, and any ordering or rounding behavior
- If the current behavior looks like a bug, pin it anyway and write it down. Fixing it is a separate change the user decides on.
- Confirm each new test actually exercises the code: break the code briefly, see the test fail, restore it

If you cannot pin behavior (no test harness, needs a live service), tell the user and agree on a manual check before continuing.

### Step 3: Move in small steps

Use one named refactoring per step: rename, extract function, inline, move, introduce parameter, replace conditional with lookup, split module. After **each** step:

1. Run the pinned tests
2. If they fail, undo the step rather than debugging forward
3. If they pass, commit (or checkpoint) with a message naming the refactoring

Prefer mechanical moves the editor or language tooling can do (rename symbol, extract method) over hand edits. Keep each diff readable on its own.

### Step 4: Watch for silent behavior changes

These change behavior without failing most tests:

- Default argument values, keyword vs. positional order
- Exception types and messages that callers match on
- Evaluation order and side effects (logging, metrics, caching, lazy initialization)
- Import-time side effects when moving code between modules
- Mutability: returning a shared list where a copy was returned before
- Iteration order of dicts and sets, sort stability, float rounding
- Public names removed from a module's exports

Check each one that applies to the code you touched.

### Step 5: Finish and report

Run the full relevant test suite, the linter, and the type checker if the project has one. Then report:

- What was restructured and why it is better (fewer lines, one responsibility per function, duplication removed)
- Confirmation that the public boundary is unchanged, with the test evidence
- Anything odd you pinned but did not fix, as a suggested follow-up

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It's just moving code, it can't break anything." | Moving code changes import order, scope, and side effects. Run the tests. |
| "I'll fix this small bug while I'm in here." | Now a test failure could mean your refactor or your fix. Do them separately. |
| "The tests pass, so it's safe." | Only if the tests cover the code you changed. Check coverage before trusting it. |
| "I'll do it in one big pass, it's faster." | One big diff is impossible to review and impossible to bisect. Small steps are faster to finish. |
| "No one calls this from outside." | You haven't searched for string and dynamic references yet. |
| "Characterization tests for buggy behavior feel wrong." | They are a measurement, not an endorsement. They let you prove the refactor changed nothing. |

## Red Flags

- A refactor diff that also changes a test's expected values
- Behavior changes and restructuring in the same commit
- Editing code that has no tests without adding any first
- Fixing a failing test by changing the assertion instead of the code
- Renaming a public symbol without a search for every reference
- A single commit touching dozens of files with no intermediate checkpoints

## Verification

- [ ] Boundary stated, and all callers (including string/dynamic references) found
- [ ] Behavior pinned by tests that were seen to fail when the code was broken
- [ ] Tests run and passing after every step, not just at the end
- [ ] Silent-change checklist (Step 4) reviewed for the code touched
- [ ] No expected values in existing tests were changed
- [ ] Report to the user includes test evidence and any pinned oddities
