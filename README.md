# My Agent Skills

Skills for AI coding agents, in the [Agent Skills](https://agentskills.io) format.

| Skill | What it does |
|---|---|
| [`codebase-onboarding`](skills/codebase-onboarding/SKILL.md) | Orients the agent in an unfamiliar repo before it changes anything: finds the real build/test commands, maps the layout, traces one code path, records baseline test failures, and writes a short verified repo map. |

## Install

Any agent supported by the [skills CLI](https://github.com/vercel-labs/skills) (Claude Code, Cursor, Codex, Copilot, and more):

```bash
npx skills add cappsryanw-prog/-my-agent-skills
```

Claude Code, manually: copy `skills/codebase-onboarding/` into `~/.claude/skills/` (all projects) or `.claude/skills/` (one project).

claude.ai: zip the `codebase-onboarding` folder and upload it under Settings → Capabilities → Skills.
