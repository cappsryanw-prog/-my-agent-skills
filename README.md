# My Agent Skills

Skills for AI agents, in the [Agent Skills](https://agentskills.io) format. Each one is a folder with a `SKILL.md` (plus scripts where a task needs deterministic tooling), and works in Claude, Claude Code, Codex, Cursor, Copilot, and any agent that reads the format.

## Skills

### Engineering discipline

| Skill | What it does |
|---|---|
| [`codebase-onboarding`](skills/codebase-onboarding/SKILL.md) | Orients the agent in an unfamiliar repo before it changes anything: finds the real build/test commands, maps the layout, traces one code path, records baseline test failures, and writes a short verified repo map. |
| [`safe-refactoring`](skills/safe-refactoring/SKILL.md) | Restructures code without changing behavior: pins current behavior with characterization tests, moves in small verified steps, and checks for silent changes (defaults, exception types, ordering, side effects). |
| [`dependency-upgrade`](skills/dependency-upgrade/SKILL.md) | Upgrades packages and runtimes safely: baseline first, changelog and breaking-change search, one package at a time with the project's own package manager, and test results compared to the baseline. |
| [`verification-before-completion`](skills/verification-before-completion/SKILL.md) | No "done", "fixed", or "passing" without fresh evidence from a command run after the last change. Covers tests, builds, bug fixes, requirements, and subagent reports. |
| [`systematic-debugging`](skills/systematic-debugging/SKILL.md) | Finds the root cause before any fix: reproduce on demand, log at each boundary to see where values go bad, test one written hypothesis at a time, fix with a failing test first, and step back after three failed fixes. |
| [`dom-text-rendering`](skills/dom-text-rendering/SKILL.md) | Puts text and symbols into a web page so they render correctly and safely: literal characters instead of HTML entities in script, text APIs for data, and HTML parsing only for trusted markup. Includes a read-only scanner for entity leaks and risky innerHTML.
| [`narrow-screen-layout`](skills/narrow-screen-layout/SKILL.md) | Keeps web layouts on screen at phone width: lets flex and grid items shrink, gives long names and URLs a place to break, wraps action rows, and contains wide tables and code. Includes a read-only Playwright checker that reports off-screen and clipped elements. |
| [`grounded-llm-prompts`](skills/grounded-llm-prompts/SKILL.md) | Writes the prompts behind AI judging features (fit verdicts, triage, scoring) so the model works from a stated fact sheet instead of inventing the user's setup, with structured output that shows its basis and a batch test for contradictions. |
| [`webapp-testing`](skills/webapp-testing/SKILL.md) | Tests local web apps with Playwright: starts dev servers, waits for real rendering, discovers selectors, captures screenshots and console errors. Includes a server helper that cleans up after itself. |

### Operations and business

| Skill | What it does |
|---|---|
| [`sop-writer`](skills/sop-writer/SKILL.md) | Turns a brain dump or call notes into a standard operating procedure a new person can follow: trigger, owner, verb-first steps, if/then decisions, a "when something goes wrong" table, and visible TBDs instead of invented details. |
| [`spreadsheet-cleanup`](skills/spreadsheet-cleanup/SKILL.md) | Cleans messy CSV/Excel exports with a script that never overwrites the original: whitespace, empty rows, duplicates, mixed date formats, and money stored as text, with guards for ZIP codes and IDs and a report of everything it changed or wasn't sure about. |

## Install

Any agent supported by the [skills CLI](https://github.com/vercel-labs/skills) (Claude Code, Cursor, Codex, Copilot, and more):

```bash
npx skills add cappsryanw-prog/-my-agent-skills
```

**Claude Code, manually:** copy a skill folder (for example `skills/safe-refactoring/`) into `~/.claude/skills/` (all projects) or `.claude/skills/` (one project).

**Claude apps (claude.ai, desktop):** zip a skill folder so the folder itself is at the root of the zip, then upload it under **Customize → Skills**. Code execution must be turned on for skills to run.

Skills with a `scripts/` folder list their Python dependencies in `scripts/requirements.txt`.

## Credits

Some skills are adapted from other open-source collections. Their original licenses apply to those folders:

- `verification-before-completion`, from [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent. MIT License.
- `systematic-debugging`, from [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent. MIT License. Supporting techniques were condensed into `references/` and examples rewritten.
- `webapp-testing`, from [anthropics/skills](https://github.com/anthropics/skills). Apache License 2.0, full text in [`skills/webapp-testing/LICENSE.txt`](skills/webapp-testing/LICENSE.txt). The server helper was rewritten to fix output-buffer hangs and orphaned child processes, and the examples were made portable. Each modified file notes its changes.

Everything else is original to this repository and released under the [MIT License](LICENSE).
