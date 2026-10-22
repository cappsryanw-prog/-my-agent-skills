---
name: skills-repo-maintainer
description: Grows and improves the cappsryanw-prog/-my-agent-skills GitHub repo by turning real lessons from use into reviewed pull requests. Use when the user asks to add, write, adapt, or improve a skill in "my skills repo" or "the agent skills repo"; when a skill from that repo gave wrong, missing, or outdated guidance during a task; when the user corrects you in a way a repo skill should have prevented; when a workflow keeps recurring that would make a good new skill; or when you find a strong public skill worth adapting. Also use at the end of any task where a repo skill was used and you noticed something it could do better.
---

# Skills Repo Maintainer

## Overview

A skills repo gets better one way: lessons from real use get folded back into it. The skill that told you to run the wrong command, the edge case it never mentioned, the correction the user had to make by hand. Those are the improvements worth having, because they came from actual work, not from guessing what a skill might need.

It also gets worse one way: drive-by edits. A rule added for one odd case, a private detail that leaks into a public file, a new skill that duplicates an old one, a change pushed straight to `main` with nobody reading it. This skill keeps the first and prevents the second. Every change starts from evidence, matches the house style, gets tested, and arrives as a pull request the owner reviews.

**Repo:** `cappsryanw-prog/-my-agent-skills` (public). Skills live in `skills/<name>/SKILL.md`, with an index in `README.md`.

## When to Use

- "Add a skill for...", "put this in my skills repo", "improve the X skill", "adapt that skill for my repo"
- While using a skill from this repo, its guidance was wrong, incomplete, outdated, or contradicted what actually worked
- The user corrected your work in a way the skill should have caught
- The same multi-step workflow has come up across several conversations and would make a good general skill
- You found a well-made public skill (with a permissive license) that fills a gap in the repo

**When NOT to use:**

- A preference that only fits this one user ("Ryan likes tables"). That belongs in memory, not a public skill.
- Anything that needs private business details to make sense (see Step 5)
- Changes to someone else's upstream repo. Suggest an issue or PR there instead.
- In the middle of another task. Finish that task first, then raise the improvement.

## The Process

### Step 1: Capture the evidence

Write down, for yourself, what happened: which skill, which instruction (quote it), what went wrong or was missing, and what actually worked. If you can't point to a concrete moment, it isn't ready to be a change yet.

### Step 2: Propose it in one line, then wait

At the end of your current task, tell the user what you noticed and what you'd change, in a sentence or two: "The `dependency-upgrade` skill never mentions peer-dependency conflicts, which is what broke today. Want me to open a PR adding that?" Do not edit the repo until they say yes. A request that already asks for the change ("add a skill for X") counts as yes.

### Step 3: Sync and read

Get the latest `main` (clone with `--depth 1`, or `git fetch origin main` in an existing clone). Then read, in full:

- `README.md`, for the skill index, categories, install notes, and credits
- The skill you're changing, every file in its folder
- For a new skill, every skill's `description` line, to check for overlap

### Step 4: Decide the shape

- **Fix or extend an existing skill** when the lesson is about that skill's job. This is the usual case.
- **Create a new skill** only when the job is distinct, would trigger on different requests, and no existing skill can absorb it without getting muddled.
- **Merge or split** only with the user's go-ahead, and say why in the PR.

Keep the change as small as the lesson. One lesson, one PR.

### Step 5: Write it in the house style

Every skill in this repo follows the same structure. Match it exactly:

```
---
name: <kebab-case, matches the folder name>
description: <what it does>. Use when <specific requests, phrases, and situations>.
---

# <Title Case Name>

## Overview              why the problem matters, how the skill solves it
## When to Use           bullets, then **When NOT to use:**
## The Process           ### Step 1: ... numbered steps
## Common Rationalizations   | Rationalization | Reality | table
## Red Flags             bullets
## Verification          - [ ] checklist
```

Voice and content rules:

- Plain, direct sentences. Explain *why* a rule exists instead of shouting it in capitals.
- Generic and reusable by anyone. Examples can be about trucking, operations, or small business, but invented, never real.
- **No private data, ever.** This repo is public. No company names, customer or driver names, rates, MC numbers, emails, internal URLs, API keys, or anything copied from a real work document. Re-read the diff for this before committing.
- Aim for 90 to 150 lines. Past about 200, move detail into a `references/` file and point to it.
- Deterministic, repetitive work goes in `scripts/`, with a `scripts/requirements.txt` for Python dependencies. Scripts never overwrite their input.

When editing an existing skill, keep its voice and structure, change only what the lesson requires, and keep every attribution line.

### Step 6: Handle adapted skills properly

When adapting a public skill:

- Confirm its license allows it (MIT, Apache-2.0, and similar). If there's no license, don't copy it; write an original skill instead.
- Add the attribution blockquote right under the title, in the existing form: `> Adapted from [<name>](<link>) in <owner/repo> (<License>). Changes: <what you changed>.`
- For Apache-2.0 and other licenses that require it, include the license file in the folder and a `license:` line in the frontmatter, as `webapp-testing` does.
- Add it to the **Credits** section of the README.

### Step 7: Test it

A skill change is not done until you've seen it work:

- Re-run the situation that surfaced the lesson (or a realistic prompt for a new skill) while following the updated skill, and confirm it now handles that case.
- Try one nearby prompt that the skill should *not* change, to make sure you didn't broaden it into nonsense.
- Run any scripts on a sample input and read the output.
- Check the frontmatter parses: `name` matches the folder, and the `description` says both what it does and when to use it.

### Step 8: Update the README

Add or update the skill's row in the right category table (create a new category only if none fits). Keep the "What it does" cell to one or two sentences in the same style as the other rows. Update Credits for adapted work.

### Step 9: Open a pull request

Never push to `main`. Work on a branch: `skill/<name>` for a new skill, `improve/<name>` for a change.

1. `git fetch origin main` and rebase if needed, so the push is small.
2. Commit with a message that says what and why: `Improve dependency-upgrade: check peer dependencies before bumping`.
3. Push the branch and open a PR. The description covers:
   - **What prompted it:** the moment from Step 1, with private details removed
   - **What changed:** the sections touched
   - **How it was tested:** what you ran and what you saw
4. Give the user the PR link in one line. They review and merge; you don't.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It's a small fix, I'll push to main." | Small fixes still change how every future run behaves. A PR costs a minute. |
| "I'll add a rule just in case." | Rules nobody needed make skills longer and worse. Change only what evidence supports. |
| "This real example makes it clearer." | The repo is public. Invent an example that teaches the same thing. |
| "I'll make a new skill, it's faster than fitting this in." | Overlapping skills fight over the same requests. Extend the existing one. |
| "I'll fix the skill now and finish the task after." | The user asked for the task. Finish it, then propose the improvement. |
| "The change obviously works." | Skills fail in ways that only show up when you follow them. Run the case. |
| "It's open source, I can copy it." | Only with a license that allows it, and only with attribution. |

## Red Flags

- Editing the repo before the user said yes
- A commit on `main`, or a PR with no testing section
- Company, customer, or people names, dollar figures, or internal links in the diff
- A new skill whose description overlaps an existing one
- A change bigger than the lesson that prompted it, or several unrelated lessons in one PR
- Capitalized MUST/NEVER rules with no reason given
- An adapted skill without its attribution line, license file, or README credit
- README table not updated for a new or renamed skill

## Verification

- [ ] The change traces to a specific moment or request, written in the PR
- [ ] The user approved the change before the repo was edited
- [ ] Structure, frontmatter, and voice match the rest of the repo
- [ ] Diff re-read for private data; none present
- [ ] Tested on the triggering case and one case it shouldn't change; scripts run
- [ ] README index and Credits are current
- [ ] Work is on a branch, rebased on fresh `main`, with a PR open and the link given to the user
