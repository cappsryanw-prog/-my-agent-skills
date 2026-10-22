---
name: verification-before-completion
description: Requires fresh evidence before any claim that work is done, fixed, or passing. Use before saying a task is complete, before committing, pushing, or opening a pull request, before moving to the next task, and before reporting what a subagent or tool did. Evidence before assertions, every time.
---

# Verification Before Completion

> Adapted from [`verification-before-completion`](https://github.com/obra/superpowers/tree/main/skills/verification-before-completion) in obra/superpowers by Jesse Vincent (MIT License). Restructured to match this repository's format.

## Overview

The most expensive words an agent can say are "Done, all tests pass" when they don't. The user stops checking, merges, and finds out later. Nearly every false completion claim has the same cause: the claim was based on what *should* be true, not on output that was just observed.

The rule is simple:

```
NO COMPLETION CLAIM WITHOUT FRESH VERIFICATION EVIDENCE
```

If you didn't run the check after your last change, you don't know the result.

## When to Use

Before any statement that implies success, including:

- "Done", "fixed", "working", "passes", "ready for review"
- Committing, pushing, opening a PR, or marking a task complete
- Moving on to the next step of a plan
- Relaying what a subagent, script, or tool reported
- Expressing satisfaction ("Great, that works") about work state

**When NOT to use:** never skip it. Scale it down for trivial changes, but a one-line change still gets the one command that proves it.

## The Process

### Step 1: Identify the proof

For each claim, name the command or observation that would prove it:

| Claim | Proof | Not proof |
|---|---|---|
| Tests pass | Test command output with 0 failures, run after the last edit | An earlier run, "should pass" |
| Build succeeds | Build command exits 0 | Linter passing, no red squiggles |
| Linter clean | Linter output with 0 errors | Running it on one file |
| Bug fixed | The original reproduction now behaves correctly | The code changed in the right spot |
| Regression test works | Test fails with the fix reverted, passes with it applied | Test passes once |
| Requirements met | Each requirement checked off against the request | Tests passing |
| Subagent finished | The diff or files show the changes | The subagent said "success" |
| Page/UI works | You loaded it and saw the result (screenshot, DOM, console) | The code compiles |

### Step 2: Run it fresh and complete

Run the full command, after your final edit, in this turn. Partial runs (one test file, one package) only prove the part they cover. Say so if that's all you ran.

### Step 3: Read the actual output

Read the output, not just the last line. Check the exit code, count failures and skips, and look for warnings that matter. "0 tests ran" is not a pass.

### Step 4: Report what the evidence shows

- If it confirms the claim: state the claim **with** the evidence ("`pytest`: 142 passed, 0 failed")
- If it doesn't: state the real status ("3 failing, here's why"), with no softening
- If you couldn't verify something: say exactly what wasn't verified and why

For requirements, re-read the original request, check each item, and list any gaps instead of saying "complete".

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It should work now." | "Should" is a prediction. Run it. |
| "I'm confident in this change." | Confidence is not evidence. |
| "I ran the tests earlier." | Earlier was before your last edit. |
| "The linter passed." | Linters don't compile, link, or run your code. |
| "The subagent said it succeeded." | Check the diff. Reports and reality diverge. |
| "It's a tiny change." | Tiny changes break builds too, and proving it takes seconds. |
| "Just this once." | That's the case this rule exists for. |

## Red Flags

- Words like "should", "probably", "seems to", or "looks correct" next to a claim
- Saying "Done!" or "Perfect!" before the verification output appears
- Committing or opening a PR without having run the checks in this session
- Repeating a tool's or subagent's success message without checking its work
- Reporting a partial check as if it were the full one
- Tests that report 0 run, or skipped tests that nobody mentioned

## Verification

- [ ] Every success claim maps to a specific command or observation
- [ ] Each check was run after the final change, in full
- [ ] Output was read: exit code, failure count, skips, relevant warnings
- [ ] The report quotes the evidence, and anything unverified is named
- [ ] Requirements were re-checked against the original request
