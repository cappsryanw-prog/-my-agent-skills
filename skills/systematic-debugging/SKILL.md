---
name: systematic-debugging
description: Finds the root cause of a bug, test failure, or unexpected behavior before any fix is written, by reproducing it, gathering evidence, and testing one hypothesis at a time. Use when something is broken, a test fails, a build or deploy errors, output is wrong, a fix didn't work, or you're about to say "let me just try changing X".
---

# Systematic Debugging

> Adapted from [`systematic-debugging`](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) in obra/superpowers by Jesse Vincent (MIT License). Changes: restructured to match this repository's format; supporting techniques condensed into `references/`; examples rewritten to be language-neutral.

## Overview

Guess-and-check debugging feels fast and isn't. Each guess changes the code, sometimes hides the symptom, and leaves the real cause in place to come back later. After three or four guesses nobody can say which change did what, and the original bug is now tangled with new ones.

The fix is to understand the failure before touching it:

```
NO FIX WITHOUT A ROOT CAUSE YOU CAN STATE AND HAVE CHECKED
```

This is faster even for simple bugs, because simple bugs have simple root causes that a few minutes of reading will show.

## When to Use

- A test fails, a build breaks, a script errors, or a page renders wrong
- Output is plausible but incorrect (wrong totals, missing rows, off-by-one dates)
- Something worked yesterday and doesn't today
- A fix you already made didn't work, or fixed one thing and broke another
- You notice yourself about to change something "to see if it helps"

**When NOT to use:** the cause is already stated and proven, such as a typo the compiler pointed to with a line number. Fix it and verify. If the first fix doesn't work, you're back in this skill.

## The Process

### Step 1: Read the whole error

Read the full message and stack trace, not just the last line. Note file paths, line numbers, error codes, and any warnings printed before the failure. The first error is usually the real one; later errors are often fallout from it.

### Step 2: Reproduce it on demand

Find the exact steps or command that triggers the failure, and run it yourself. If it only happens sometimes, that is a clue (timing, shared state, order of tests, environment), not a reason to start guessing. Gather more data until you can make it happen. See `references/flaky-failures.md`.

### Step 3: Check what changed

Look at recent commits, the diff, dependency or lockfile changes, config and environment variables, and data inputs. Compare against the last known good state. "Nothing changed" is rarely true; find out what did.

### Step 4: Find where it breaks

When the work passes through several pieces (form → API → database, export → script → spreadsheet, CI → build → deploy), don't guess which piece is wrong. Add a temporary log or print at each boundary showing what goes in and what comes out, run once, and read where the values turn bad. Then focus on that one piece.

When the error shows up deep in the code, trace the bad value backward: what passed it in, and what passed it to that, until you reach where it was first created. Fix it there, not where it finally crashed. See `references/root-cause-tracing.md`.

### Step 5: Compare against something that works

Find similar code, a similar record, or an earlier version that behaves correctly. List every difference between working and broken, including the ones that "can't matter". If you're following a pattern from documentation or another file, read the reference fully rather than skimming.

### Step 6: Test one hypothesis

Write it down in one sentence: "The total is wrong because refunds are stored as positive numbers and the report adds them." Then make the smallest change or check that would prove or disprove it, changing one thing only. If it's wrong, discard it and form a new one from what you learned. Don't stack a second guess on top of the first.

If you don't understand part of the system, say so plainly and go read or ask, rather than trying changes and hoping.

### Step 7: Fix with a failing test first

Before fixing, write the smallest test or script that reproduces the bug and fails. Then make one change that addresses the root cause, with no unrelated cleanup bundled in. Run the reproduction (it should now pass) and the full test suite (nothing else should break). Confirm with fresh output before saying it's fixed, as `verification-before-completion` describes.

### Step 8: Stop after three failed fixes

If three fixes have each failed, or each one surfaces a new problem somewhere else, the problem is probably the design, not the latest detail. Stop fixing. Write up what you tried, what each attempt revealed, and what you now think is structurally wrong, and discuss it with the user before trying a fourth.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It's simple, I can see the problem." | Seeing the symptom isn't knowing the cause. Checking takes a minute. |
| "This is urgent, no time to investigate." | Guessing under pressure is how one bug becomes three. |
| "I'll try this quick change first." | The first guess sets the pattern for the whole session. |
| "I'll change a few things at once to save time." | Then you can't tell which change mattered, or which one broke something else. |
| "I'll write the test after it's working." | A test written after a fix often can't fail. Write it first and watch it fail. |
| "One more attempt." (after two or three) | Repeated failed fixes point at the design. Step back. |
| "It must be environmental, nothing to find." | Most "no root cause" conclusions are unfinished investigations. |

## Red Flags

- Proposing a fix before reproducing the failure
- "Let's try X and see if it works"
- Several changes made between test runs
- Explaining the bug with "probably" or "might be"
- Fixing at the line that crashed without asking where the bad value came from
- A fourth fix attempt without stepping back
- The user asking "did you check that?" or "stop guessing"

If the investigation truly shows the cause is outside your control (a third-party outage, a timing limit you can't change), say so, document what you ruled out, and add handling (a retry, a clear error, logging) rather than a silent workaround.

## Verification

- [ ] The failure was reproduced before any fix
- [ ] The root cause is stated in one sentence and was confirmed, not assumed
- [ ] A test or script reproduced the bug and failed before the fix
- [ ] One change was made, aimed at the cause rather than the symptom
- [ ] The reproduction now passes and the full suite was run fresh
- [ ] Temporary logging added during investigation was removed
