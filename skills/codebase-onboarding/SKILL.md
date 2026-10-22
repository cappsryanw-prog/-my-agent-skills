---
name: codebase-onboarding
description: Orients an agent in an unfamiliar repository before it changes anything, producing a short verified map of how to build, test, and navigate the code. Use when starting work in a repo you have not seen before, when a task touches a part of the codebase you have not read, when you are about to guess a build or test command, or when the user asks "how does this project work?" or "get familiar with this repo".
---

# Codebase Onboarding

## Overview

Most bad changes in an unfamiliar codebase come from guessing: the wrong test command, a helper that already exists but was rewritten, a convention that was ignored, a file that is generated and gets overwritten on the next build. A senior engineer joining a project spends the first hour reading, running, and taking notes before touching anything.

This skill makes that first hour explicit and short. You discover how the project builds and tests, where the important code lives, and what conventions it follows. Then you prove the build and tests actually run, and write the findings down in a compact map you and the user can rely on.

## When to Use

- First task in a repository you have not explored in this session
- The task touches a directory, service, or package you have not read yet
- You are about to run a command (`npm test`, `make`, `pytest`) based on what projects *usually* do rather than what this one does
- The user asks you to "get familiar with", "explore", or "explain" a repo

**When NOT to use:**

- You already onboarded to this repo in this session and the map is still accurate
- The task is a one-line, self-contained edit where the file and change are fully specified ("fix the typo in README line 12")
- The repo already has an up-to-date onboarding doc (`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`) that you have read and verified. Run Step 4 to confirm it, then stop.

## The Process

Time-box it. For most repos, Steps 1–5 should take minutes, not an hour. Skim, don't read every file.

### Step 1: Read what the project says about itself

Read these if they exist, in this order, and stop reading a file once it stops being relevant:

1. Agent instruction files: `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/`, `.github/copilot-instructions.md`
2. `README.md`, then `CONTRIBUTING.md` and anything under `docs/` with "setup", "development", or "architecture" in the name
3. The manifest(s): `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `Gemfile`, `*.csproj`
4. Task runners: `Makefile`, `justfile`, `Taskfile.yml`, the `scripts` block of `package.json`
5. CI config: `.github/workflows/`, `.gitlab-ci.yml`, `.circleci/`. **CI is the most reliable source of the real build and test commands**, because it has to work.

Write down every command you find for install, build, test, lint, and run, and note where it came from.

### Step 2: Map the layout

List the top two levels of the tree, ignoring dependency and build output (`node_modules`, `vendor`, `dist`, `build`, `target`, `.venv`). For each top-level directory, write one line on what it holds.

Then identify:

- **Entry points**: `main` functions, server startup, CLI definitions, route tables, the `bin`/`main`/`exports` fields of the manifest
- **Generated code**: anything with a "do not edit" header, or produced by codegen (protobuf, OpenAPI, ORM migrations, lockfiles). Never hand-edit these. Find the source and the command that regenerates them.
- **Monorepo boundaries**: workspaces, packages, or services that build and test independently

### Step 3: Trace one real path

Pick one feature relevant to your task and follow it end to end. For example, follow one HTTP request from route to handler to data access to response, or one CLI command from argument parsing to output. Read the actual code, not just the file names.

This teaches you the project's real patterns: how errors are handled, how config is loaded, how dependencies are wired, and where the tests for that path live.

### Step 4: Prove the build and tests run

Run the install, build, and test commands you found, in that order. Prefer the narrowest test command that exercises the area you will touch, and run the full suite only if it is fast.

Record the outcome honestly:

- **Passes**: note the command and roughly how long it took
- **Fails before you changed anything**: this is the baseline. Record which tests fail and the error. You must not later claim these failures as yours, or hide behind them.
- **Cannot run** (missing service, secret, or toolchain): say exactly what is missing and ask the user. Do not invent a workaround that changes project config.

### Step 5: Extract the conventions

From the code you read in Step 3 and two or three neighboring files, note:

- Naming, file layout, and how new modules are added
- Error handling and logging style
- Test framework, where tests live, and how they are named
- Formatter and linter config (`.editorconfig`, `.prettierrc`, `ruff.toml`, `.eslintrc*`, `rustfmt.toml`)
- Existing helpers and utilities that your task might otherwise duplicate. Search for them by keyword before writing new ones.

### Step 6: Write the map

Produce a short map, under about 40 lines, and share it with the user before starting the task:

```
REPO MAP: <project name>
Purpose:       <one sentence>
Stack:         <language, framework, key libraries>
Install:       <command>            (source: <file>)
Build:         <command>            (verified ✓ / failed ✗ / not run)
Test:          <command>            (verified ✓, ~Ns, N baseline failures)
Lint/format:   <command>
Layout:
  <dir>/       <what it holds>
  ...
Entry points:  <files>
Generated:     <paths and the command that regenerates them>
Conventions:   <3–6 bullets>
Unknowns:      <what you could not verify and why>
```

If the user wants it kept, save it where the project already keeps agent context (for example `CLAUDE.md` or `AGENTS.md`). Ask before creating or editing that file.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It's a Node project, so the test command is `npm test`." | Many projects use `pnpm`, workspaces, a Makefile, or a custom script. CI config tells you the truth in seconds. |
| "I'll learn the codebase as I go." | You will learn it by breaking it. Tracing one path first is cheaper than reverting a change built on a wrong assumption. |
| "The tests were already failing, so my change is fine." | Only if you recorded the baseline *before* changing anything. Otherwise you cannot tell your failures from pre-existing ones. |
| "Reading the README is enough." | READMEs go stale. Commands are only facts once you have run them. |
| "This helper doesn't exist, so I'll write one." | You haven't searched yet. Duplicate utilities are one of the most common review comments on agent-written code. |
| "Onboarding takes too long for a small task." | Scale it down, but don't skip it. Steps 1 and 4 alone take a couple of minutes and prevent the most expensive mistakes. |

## Red Flags

- Running a build or test command you did not find in the repo
- Editing a file with a "generated" or "do not edit" header
- Writing a new utility without searching for an existing one
- Reporting "tests pass" without having run them, or without noting baseline failures
- Introducing a new library, pattern, or file layout the project doesn't already use
- Reading dozens of files without writing anything down; onboarding should end in a map, not a tour
- Changing project config (lockfiles, CI, tool versions) just to make the build run locally

## Verification

Before starting the actual task, confirm:

- [ ] Install, build, and test commands are identified, each with its source file
- [ ] The build and the relevant tests were actually run, and the result is recorded (including baseline failures)
- [ ] Entry points and generated-code locations are identified
- [ ] At least one real code path relevant to the task was traced end to end
- [ ] Conventions are noted from real files, not assumed
- [ ] A repo map was shared with the user, with unknowns listed explicitly
