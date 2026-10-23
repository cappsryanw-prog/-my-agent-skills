---
name: grounded-llm-prompts
description: Writes the prompts inside an app or script that ask an AI model to judge, score, or recommend things for a specific person or business, so the model works from stated facts instead of inventing them. Use when building or fixing a feature that sends items to an LLM for a fit verdict, triage, ranking, or "is this useful for us?" analysis; when model output contradicts itself across items; or when it states things about the user's setup, tools, or history that nobody told it.
---

# Grounded LLM Prompts

## Overview

When a prompt says "decide whether this is useful for my workflow" and never describes the workflow, the model doesn't stop and ask. It fills the gap with a plausible guess, and it guesses fresh on every call. One verdict says the invoices are already automated, the next treats invoicing as an unsolved problem. Each answer sounds confident, so the contradiction only shows when you read several side by side.

The fix is to stop asking the model to know things it can't know. Put the facts it needs in the prompt as a short, explicit fact sheet, tell it what to do when a fact is missing, and make it show which fact each claim rests on. Then test across a batch of items, because a single good answer proves nothing about consistency.

## When to Use

- Writing or changing a prompt that evaluates items (tools, leads, tickets, vendors, articles) against a user's or company's situation
- Output that says "you already do X" or "since you use Y" when X and Y were never given
- Verdicts that contradict each other across items in the same run
- Adding personalization ("for my team", "for my stack") to an AI feature
- Reviewing a diff that adds an LLM call returning a recommendation or score

**When NOT to use:**

- One-off chat questions where the person can correct the answer in the next message
- Open-ended creative or brainstorming prompts, where invention is the point
- Retrieval pipelines that already pass source documents; follow that system's citation design instead

## The Process

### Step 1: List what the model would have to know

Read the task in the prompt and write down every fact a good answer depends on. For "does this tool fit us?" that is usually: what the business does, the tools and languages in use, what is already automated, what is still manual or painful, hard constraints (budget, platform, no new languages), and what "useful" means here. Anything on that list the prompt doesn't state, the model will invent.

### Step 2: Write a fact sheet, with status

Put the facts in one labeled block near the top of the prompt. State each one plainly, and mark status where it matters so the model can't blur them together:

```text
<context>
Business: 6-person delivery company. Staff are not developers.
Stack: Python scripts, Excel, Microsoft 365. No Go, no .NET.
Already automated: daily route export -> spreadsheet (Python).
Still manual: matching invoices to delivery records.
Not used: any CRM.
Useful means: saves staff time this quarter without a new language.
</context>
```

Keep it short and true. Load it from one config file or setting, not copy-pasted into each prompt, so every call sees the same facts and updating them is one edit.

### Step 3: Say what to do with gaps

Tell the model the fact sheet is the only source of truth about the user, and give it a permitted move when it's not enough: "If the answer depends on something not in <context>, say what is unknown instead of assuming." A model with no allowed way to say "I don't know" will guess.

### Step 4: Ask for structured output that shows its basis

Request a fixed shape, for example JSON with `verdict`, `reason`, `facts_used`, and `unknowns`. `facts_used` should quote or name lines from the fact sheet. This turns invention into something you can spot: a claim with no matching fact, or a fact quoted that isn't in the sheet. Validate the shape in code and treat a parse failure as a failure, not a blank verdict.

Lower the temperature for judging tasks. It reduces drift between calls, though it never replaces the fact sheet.

### Step 5: Test across a batch, not one item

Run the prompt on at least five varied items in one go, including one that touches something the fact sheet marks as already automated and one it doesn't cover at all. Read the results side by side and check:

- Every claim about the user traces to a line in the fact sheet
- No two results disagree about the same fact
- The uncovered item produces an `unknowns` entry, not a guess

Run the batch twice. If verdicts flip with no change in input, tighten the facts or the criteria before shipping.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The model is smart, it'll figure out our context." | It can't know facts it was never given. It will produce something plausible and different each time. |
| "One sample answer looked right." | Invention shows up as inconsistency across items. Test a batch. |
| "I'll put the context in a long paragraph." | Prose blurs "done" and "still manual". Short labeled lines keep status unambiguous. |
| "Asking for 'unknowns' makes answers weaker." | An honest "unknown" is fixable. A confident wrong verdict misleads silently. |
| "I'll paste the context into each prompt." | Copies drift. One source loaded everywhere stays consistent. |

## Red Flags

- Phrases like "my workflow", "our stack", or "what we do" with no definition anywhere in the prompt
- Output that mentions tools, systems, or history absent from the prompt
- Two items in one run that describe the same fact differently
- Free-text verdicts with no field showing what they were based on
- Context duplicated across several prompt strings in the code
- A prompt verified on a single example

## Verification

- [ ] Every fact the task depends on is in one fact sheet, with status (done, manual, not used) where relevant
- [ ] The fact sheet loads from a single source shared by every call
- [ ] The prompt names the fact sheet as the only source of truth and allows "unknown"
- [ ] Output is structured with `facts_used` and `unknowns`, and the code validates it
- [ ] A batch of at least five varied items, run twice, shows no invented or contradictory claims
