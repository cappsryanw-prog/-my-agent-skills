# Anthropic Example Skills (vendored)

Unmodified copies of the open-source skills from [anthropics/skills](https://github.com/anthropics/skills), taken from commit [`dbd4588`](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44) (October 2026). They are kept here as-is for reference and installation. They are not written in this repo's house style, and none of them have been edited.

Each skill is licensed under the Apache License 2.0. The full text is in each folder's `LICENSE.txt`. Third-party components bundled with some of them (fonts, FFmpeg, imageio, and others) are listed in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## What's here

| Skill | What it does |
|---|---|
| [`academy-guide`](academy-guide/SKILL.md) | Points people to matching Claude Academy courses and tutorials when they ask how to use Claude. |
| [`algorithmic-art`](algorithmic-art/SKILL.md) | Generative art in p5.js with seeded randomness and adjustable parameters. |
| [`brand-guidelines`](brand-guidelines/SKILL.md) | Applies Anthropic's brand colors and typography. Useful as a template for writing your own brand skill. |
| [`canvas-design`](canvas-design/SKILL.md) | Original posters and static visual pieces as PNG or PDF, starting from a written design philosophy. Bundles open-licensed fonts. |
| [`claude-api`](claude-api/SKILL.md) | Reference for the Claude API and Anthropic SDKs: models, parameters, streaming, tool use, caching, and agents. |
| [`discernment-nudge`](discernment-nudge/SKILL.md) | Adds two or three specific follow-up questions after advice or a draft, so the user checks it before acting on it. |
| [`frontend-design`](frontend-design/SKILL.md) | Guidance for distinctive UI design: aesthetic direction, typography, and avoiding templated defaults. |
| [`internal-comms`](internal-comms/SKILL.md) | Formats for internal communications such as status reports, leadership updates, newsletters, and FAQs. |
| [`mcp-builder`](mcp-builder/SKILL.md) | Builds MCP servers in Python (FastMCP) or TypeScript, with tool-design guidance and an evaluation harness. |
| [`skill-creator`](skill-creator/SKILL.md) | Creates and improves skills, runs evals, benchmarks performance, and tunes descriptions so skills trigger correctly. |
| [`slack-gif-creator`](slack-gif-creator/SKILL.md) | Animated GIFs sized and validated for Slack. |
| [`theme-factory`](theme-factory/SKILL.md) | Ten preset color and font themes, or a new one on request, applied to slides, docs, or pages. |
| [`web-artifacts-builder`](web-artifacts-builder/SKILL.md) | Multi-component React, Tailwind, and shadcn/ui apps bundled into a single HTML file. |

`webapp-testing` is also from anthropics/skills. It lives in [`skills/webapp-testing`](../../skills/webapp-testing/) because it was adapted, so it isn't duplicated here.

## Installing

A plain `npx skills add cappsryanw-prog/-my-agent-skills` skips this folder. Add `--full-depth` to include it, or add `--skill <name>` as well to install just one. To install one by hand, copy its folder into `~/.claude/skills/`.

## Not included

- `docx`, `pdf`, `pptx`, and `xlsx` are source-available under Anthropic's proprietary license ("All rights reserved"), so they can't be redistributed here.
- `doc-coauthoring` has no license file, so it isn't copied either.

## Updating

To refresh from upstream, replace each folder with the version from the new commit, update the commit link above, and note anything that was added or removed in the pull request.
