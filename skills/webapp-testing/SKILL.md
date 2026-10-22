---
name: webapp-testing
description: Tests and debugs local web applications with Playwright, starting dev servers, inspecting the rendered page, clicking through flows, and capturing screenshots and console logs. Use when asked to test, verify, or debug a web UI, check that a page or form works, reproduce a frontend bug, or confirm a change renders correctly before calling it done.
license: Apache-2.0. Complete terms in LICENSE.txt
---

# Web App Testing

> Adapted from [`webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) in anthropics/skills (Apache License 2.0). Changes: restructured to this repository's format; `scripts/with_server.py` rewritten so it can't hang on server output and doesn't leave child processes running; examples made portable. See the header of each file for details.

## Overview

"The code compiles" says nothing about whether a button works. The only way to know a web UI behaves correctly is to load it in a real browser and look. This skill does that with Python Playwright scripts: start the app, wait for it to actually render, discover the real selectors, act, and capture evidence (screenshots, console output, DOM state).

## When to Use

- Verifying that a page, form, or flow works after a change
- Reproducing or debugging a frontend bug
- Capturing screenshots or browser console errors
- Smoke-testing a local dev server before reporting a task done

**When NOT to use:**

- The project already has an end-to-end suite (Playwright Test, Cypress). Run and extend that instead of writing one-off scripts.
- Load testing, or automating third-party sites you don't control

## Setup

```bash
pip install playwright
playwright install chromium   # skip if a Chromium build is already provided
```

## The Process

### Step 1: Pick the approach

```
Static HTML file?
├─ Yes → Read the HTML for selectors, open it with a file:// URL
│        (see examples/static_html_automation.py)
└─ No → Is the dev server already running?
    ├─ No  → Use scripts/with_server.py to start it (Step 2)
    └─ Yes → Go straight to Step 3
```

### Step 2: Start servers with the helper

Run `python scripts/with_server.py --help` first. Treat the script as a black box; there is no need to read its source to use it.

```bash
# One server
python scripts/with_server.py --server "npm run dev" --port 5173 -- python check_ui.py

# Backend + frontend
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python check_ui.py
```

It waits until each port accepts connections, runs your command, then stops every server and its child processes. Server output goes to log files; if a server dies on startup, the helper prints the end of its log.

### Step 3: Reconnaissance, then action

Never guess selectors from source code for a dynamic app. Look at what actually rendered:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))

    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")       # let client-side JS finish

    page.screenshot(path="before.png", full_page=True)
    print(page.get_by_role("button").all_inner_texts())  # discover real selectors

    page.get_by_role("button", name="Save").click()
    page.get_by_text("Saved").wait_for()          # wait for the result, not a fixed delay
    page.screenshot(path="after.png", full_page=True)

    print("console errors:", errors)
    browser.close()
```

See `examples/element_discovery.py` and `examples/console_logging.py` for fuller versions.

### Step 4: Report with evidence

Report what you observed: the screenshots taken, the console errors (or that there were none), and whether each expected element or state appeared. If something failed, include the error and the screenshot path.

## Selector and Waiting Rules

- Prefer user-facing locators: `get_by_role`, `get_by_label`, `get_by_text`, `get_by_test_id`. Use CSS only when those don't fit.
- Wait for a **condition** (`locator.wait_for()`, `expect(...)`, `wait_for_url`), not a fixed `wait_for_timeout`. Fixed sleeps make scripts slow and flaky.
- Wait for `networkidle` before inspecting a dynamic page. Inspecting first is the most common cause of "element not found".
- Run headless and always close the browser.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The component compiles, so the page works." | Rendering, routing, and data loading fail at runtime. Load the page. |
| "I know the selector from the JSX." | Rendered DOM often differs (portals, generated classes, conditional rendering). Inspect first. |
| "I'll add a 3-second sleep to be safe." | Wait for the element or state you need. Sleeps are flaky in both directions. |
| "No errors were thrown, so it's fine." | Check the browser console. Many frontend failures only log there. |

## Red Flags

- Reporting that a UI works without a screenshot, DOM check, or console capture
- `wait_for_timeout` used as the main synchronization method
- Inspecting the DOM before `networkidle` on a client-rendered app
- Leaving a dev server running after the script ends (use the helper)
- Selectors copied from source code without checking the rendered page

## Verification

- [ ] The app was loaded in a real (headless) browser, not assumed to work
- [ ] Selectors came from the rendered page
- [ ] Waits are condition-based
- [ ] Console errors were captured and reported
- [ ] Screenshots or DOM assertions back up every claim
- [ ] All servers were stopped afterward
