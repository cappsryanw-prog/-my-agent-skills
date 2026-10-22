---
name: sop-writer
description: Turns a process someone describes (a brain dump, call notes, a screen recording transcript, or "here's how I do it") into a clear standard operating procedure (SOP) a new person can follow without asking questions. Use when asked to write, document, or clean up an SOP, process doc, checklist, playbook, runbook, work instruction, or training guide for a business or operations task.
---

# SOP Writer

## Overview

Most process docs fail the same test: a new hire can't do the task from them. They describe the happy path in the expert's shorthand, skip the decisions the expert makes without thinking, and say nothing about what to do when something goes wrong. The expert reads the doc and it looks complete, because the expert already knows the missing parts.

This skill writes SOPs for the person who doesn't know the missing parts. It pulls out the trigger, owner, inputs, decisions, and exceptions, writes each step as one verifiable action, and lists what's still unknown instead of guessing.

## When to Use

- "Write an SOP for...", "document how we...", "turn this into a checklist"
- Cleaning up an existing process doc that people don't follow
- Handing a task to a new hire, a backup person, or an assistant
- Before automating a process. You can't automate a process nobody has written down.

**When NOT to use:**

- Policy documents (what is allowed) rather than procedures (how to do it)
- Software runbooks that are mostly commands. Write those next to the code, in its repo.

## The Process

### Step 1: Get the raw process

Work from what the user gives you: notes, a transcript, an email thread, an old doc, or a description. If it's thin, ask for one real recent example: "Walk me through the last time you did this, start to finish." A specific instance surfaces details a general description skips.

### Step 2: Extract the frame

Before writing steps, pin down:

- **Purpose:** why this process exists, in one sentence
- **Trigger:** what starts it (a time, an email, a request, a status change)
- **Owner:** the role that does it, plus the backup (roles, not just names, so the doc survives turnover)
- **Inputs:** documents, data, and access needed before starting (systems, logins, templates)
- **Output / done means:** the observable end state ("invoice sent and logged in the tracker")
- **Frequency and time:** how often, and roughly how long it takes

### Step 3: Write the steps

- One action per step, starting with a verb: "Open", "Enter", "Check", "Send"
- Name the exact screen, field, button, file, or person. "Update the system" is not a step.
- Put decisions inline as **If / then**: "If the rate is over $3.00/mile, get manager approval before booking."
- Add a **check** after any step where a mistake is expensive or hard to undo: what to look at to confirm it worked
- Use numbered sub-steps for detail, and keep the main list to roughly 5–15 steps. Split a longer process into separate SOPs.
- Write for someone competent but new: no unexplained acronyms or internal nicknames (define them in a glossary)

### Step 4: Cover what goes wrong

Ask, or infer from the material: what are the two or three most common problems? For each one, write what you see, what to do, and who to escalate to and when. This section is what makes an SOP usable on a bad day.

### Step 5: Mark the gaps

Never invent a value, threshold, system name, or contact. If the source doesn't say, write `[TBD: who approves refunds over $500?]` and list every TBD at the top of your reply so the user can fill them in.

### Step 6: Assemble it

Use this structure:

```
# <Process name>
Purpose:     <one sentence>
Owner:       <role> (backup: <role>)
Trigger:     <what starts it>
Frequency:   <how often> · Time: <about how long>
Done means:  <observable end state>

## Before you start
- <access, files, information needed>

## Steps
1. <Verb> <exact action>.
   - If <condition>, <action>.
   - Check: <how to confirm it worked>.
2. ...

## When something goes wrong
| You see | Do this | Escalate to |
|---|---|---|

## Glossary          (only if needed)
## Revision history  (date · change · by whom)
```

Deliver it in the format the user will keep it in: a document, a wiki page, or a one-page checklist version for daily use.

### Step 7: Walk-through test

Read the SOP as a new hire. For each step, ask: "Could I do this without asking anyone?" If not, fix the step or add a TBD. If possible, suggest the user have someone unfamiliar with the task try it once and mark where they got stuck.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Everyone knows that part." | New people don't, and they're who the SOP is for. Write it down. |
| "I'll fill in a reasonable threshold." | An invented number becomes policy the day someone follows it. Mark it TBD. |
| "Exceptions make it too long." | The exception table is what people open the SOP for. Keep the steps short instead. |
| "One big SOP is easier to find." | A 40-step doc doesn't get followed. Split it at natural handoffs. |
| "Use the person's name as owner." | People leave and roles stay. Name the role, and the person in parentheses if helpful. |

## Red Flags

- Steps like "process the order" or "update the system" with no screen, field, or action named
- No trigger, owner, or definition of done
- No "when something goes wrong" section
- Values, approvers, or system names that weren't in the source material and aren't marked TBD
- Acronyms or internal nicknames a new hire wouldn't know
- More than about 15 top-level steps in one SOP

## Verification

- [ ] Purpose, owner and backup, trigger, frequency, and "done means" are all filled in or marked TBD
- [ ] Every step is one action starting with a verb and naming the exact place it happens
- [ ] Decisions are written as If / then, and costly steps have a Check
- [ ] At least the most common failure cases are covered, with escalation
- [ ] Nothing is invented; every gap is a visible TBD, listed for the user
- [ ] Walk-through test done from a new hire's point of view
