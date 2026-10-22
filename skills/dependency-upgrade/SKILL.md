---
name: dependency-upgrade
description: Upgrades a project dependency, runtime, or framework version safely by reading the changelog for breaking changes, upgrading in isolated steps, and proving the build and tests still pass. Use when asked to bump, update, or upgrade a package, fix a security advisory (npm audit, Dependabot, pip-audit), move to a new major version, or update a language runtime or lockfile.
---

# Dependency Upgrade

## Overview

"Just bump the version" is how a Friday deploy breaks. Upgrades fail in predictable ways: a major version renames an API, a transitive dependency jumps along with it, the lockfile and the manifest disagree, a peer dependency no longer fits, or the new version needs a newer runtime than production has.

This skill treats an upgrade as a small, reviewable change with evidence. Read what changed, change one thing at a time, and prove the project still works.

## When to Use

- Bumping a package, framework, SDK, or language runtime version
- Responding to a security advisory or a Dependabot/Renovate PR
- Regenerating or repairing a lockfile
- A build broke after dependencies changed

**When NOT to use:**

- Adding a brand-new dependency. Ask first whether the project already has something that does the job.
- The project pins versions on purpose for a documented reason, and the user hasn't asked to change that

## The Process

### Step 1: Establish the baseline

Before touching anything, run install, build, and tests on the current versions and record the result, including any failures that already exist. Note the runtime version (`node -v`, `python --version`) and the package manager the project actually uses: the lockfile tells you (`package-lock.json` → npm, `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `poetry.lock` → Poetry, `uv.lock` → uv).

Never mix package managers. Using npm in a pnpm project rewrites the dependency tree.

### Step 2: Scope the change

Find out exactly what will move:

- Current version, target version, and whether it crosses a **major** version (semver breaking change)
- Why the upgrade is wanted: security fix, needed feature, end of support
- The smallest version that satisfies that need. For a security fix this is often a patch release, not the latest major.
- What else moves with it: run the package manager's dry-run or "why" command (`npm ls <pkg>`, `pnpm why <pkg>`, `pip install --dry-run`, `cargo tree -i <pkg>`) to see dependents and peers

### Step 3: Read what changed

For each version boundary crossed, read the changelog, release notes, or migration guide. Search the project's code for every API the notes mark as removed, renamed, or changed in behavior. List each hit with its file and line.

Also check:

- Required runtime version (`engines`, `python_requires`, `rust-version`). Will production and CI still satisfy it?
- Peer dependency ranges that other packages in the project require
- Changed defaults (timeouts, strict modes, ESM vs. CommonJS, TLS settings), which break things without a compile error

### Step 4: Upgrade in isolated steps

- One package (or one tightly coupled group, like `react` + `react-dom`) per change
- For a multi-major jump, step through each major if the migration guides are written that way
- Use the package manager's own command (`npm install pkg@x.y.z`, `poetry add pkg@^x.y`), so the manifest and lockfile stay consistent. Don't hand-edit the lockfile.
- Apply the code changes from Step 3, then build and run tests

If tests fail, separate the cause: a real incompatibility (fix the code), a test relying on old behavior (update the test, and explain why), or a pre-existing failure from the baseline (leave it alone).

### Step 5: Verify and report

Run install from a clean state if practical (delete `node_modules` or the virtualenv, reinstall from the lockfile), then build, test, and lint. Start the app or run a smoke test if the dependency affects runtime behavior.

Report:

- `<package>: <old> → <new>`, and anything else that moved in the lockfile
- Breaking changes found and how each was handled, with file references
- Test results compared to the baseline
- Anything not verified (no test coverage for a changed API, a runtime mismatch in production)

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It's a minor version, nothing breaks." | Semver is a promise, not a guarantee, and many packages don't follow it. Read the notes. |
| "I'll upgrade everything at once to save time." | When something breaks you won't know which package caused it. |
| "The lockfile conflict is easier to fix by hand." | Hand-edited lockfiles produce trees no tool can reproduce. Regenerate with the package manager. |
| "Latest is always best for security." | The fix is usually in a patch release. Jumping majors adds risk the advisory didn't require. |
| "Tests pass, ship it." | Only if the tests touch the changed APIs. Check the Step 3 hit list against coverage. |
| "`--force` / `--legacy-peer-deps` makes the error go away." | It hides a real version conflict that will surface at runtime. Resolve it or tell the user. |

## Red Flags

- Running a package manager that doesn't match the project's lockfile
- `--force`, `--legacy-peer-deps`, or `--no-verify` used to get past an error
- A diff where the lockfile changes hundreds of unrelated packages
- Upgrading across a major version without having read its migration guide
- Deleting a lockfile to "fix" an install
- Claiming success without comparing test results to the baseline

## Verification

- [ ] Baseline install/build/test result recorded before the change
- [ ] Target version chosen deliberately (smallest that meets the need)
- [ ] Changelog/migration notes read for every boundary crossed; affected code located
- [ ] Runtime and peer dependency requirements checked
- [ ] Manifest and lockfile updated by the package manager, not by hand
- [ ] Build and tests run after the upgrade and compared to the baseline
- [ ] Report lists versions moved, breaking changes handled, and anything unverified
