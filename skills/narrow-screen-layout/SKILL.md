---
name: narrow-screen-layout
description: Builds and fixes web layouts so content fits a phone-width screen without running off the right edge, clipping text, or hiding buttons. Use when writing CSS or markup for cards, lists, flex or grid rows, tables, or code blocks; when a page scrolls sideways or content is cut off on mobile; when long names, URLs, IDs, or API or AI text break a layout; or when checking a new page at phone width.
---

# Narrow Screen Layout

## Overview

Most sideways overflow on phones comes from a handful of CSS defaults that stay invisible on a laptop: flex and grid items that refuse to shrink below their content, a long word with nowhere to break, a fixed width, padding added on top of `width: 100%`, and rows that never wrap. A 1400px monitor has room to hide all of them. At 375px, one long name or URL pushes a card past the screen edge, and whatever sits to its right, often the action button, is cut off.

The usual quick fix, `overflow-x: hidden` on the body, makes it worse. The sideways scroll goes away, but the clipped content becomes unreachable. This skill fixes the cause instead: assume text of any length, let containers shrink, let rows wrap, and check the real page at phone width.

## When to Use

- Building cards, list items, headers, toolbars, or any flex or grid row
- Showing text whose length you don't control: names, URLs, emails, IDs, hashes, API or model output
- Adding tables, code blocks, images, embeds, or charts to a page
- A page scrolls sideways, or text or buttons are cut off, on a phone
- Reviewing a fix that adds `overflow-x: hidden` or `white-space: nowrap`

**When NOT to use:**

- Content that is meant to scroll sideways (carousels, wide data grids). Give it its own scroll box (Step 5) and leave it alone.
- Mobile redesigns: navigation patterns, breakpoint strategy, touch target sizing. That is design work beyond keeping content on screen.
- Native mobile apps

## The Process

### Step 1: Confirm the page declares a viewport

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

Without it, phones lay the page out about 980px wide and shrink it to fit. Nothing overflows, but everything is tiny and media queries never fire. Don't add `maximum-scale=1` or `user-scalable=no`; they block zoom for people who need it.

### Step 2: Set the base rules once

```css
*, *::before, *::after { box-sizing: border-box; }
img, video, canvas, svg { max-width: 100%; height: auto; }
iframe { max-width: 100%; }
```

`border-box` keeps `width: 100%` at 100% after padding and borders. The media rule lets a 1200px screenshot shrink to the screen instead of stretching it.

### Step 3: Let flex and grid children shrink

A flex item defaults to `min-width: auto`, so it can't get narrower than its longest word. A grid `1fr` column behaves the same way. One long word and the whole row grows past the screen. Give text-holding children permission to shrink:

```css
.row        { display: flex; gap: .75rem; }
.row > .body { flex: 1; min-width: 0; }
.layout     { display: grid; grid-template-columns: minmax(0, 1fr) auto; }
.cards      { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(16rem, 100%), 1fr)); }
```

`min(16rem, 100%)` stops a card's minimum width from being wider than the phone itself.

### Step 4: Give long text somewhere to break

Any text you didn't write might be a single 60-character "word". Let it break where it lands:

```css
.body { overflow-wrap: anywhere; }
```

`anywhere` also lowers the element's minimum size, so unlike `break-word` it works inside flex items. If one line is the design (a title in a list), truncate on purpose with `white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0`, and make the full text reachable (a detail view or `title` attribute). Keep `word-break: break-all` for hashes and IDs; it splits ordinary words mid-letter.

### Step 5: Let rows wrap, and contain what can't shrink

- Rows that hold actions get `flex-wrap: wrap`, so a button drops to the next line instead of off the screen. Avoid `white-space: nowrap` on anything that holds data.
- Replace fixed widths with capped ones: `width: min(28rem, 100%)` or `max-width: 28rem`, not `width: 28rem`.
- Use `100%`, not `100vw`, for full width. `100vw` includes the scrollbar on desktop and adds a sliver of overflow.
- Tables, `pre` blocks, and wide charts go in their own scroll box, so only that box scrolls and the page stays put:

```css
.scroll-x { overflow-x: auto; max-width: 100%; }
pre       { overflow-x: auto; }
```

### Step 6: Check at phone width with worst-case content

Load the real page at 320 and 375 pixels wide, filled with the longest realistic content: long names, an unbroken URL, a paragraph of model output, many tags. Then run the checker:

```bash
pip install -r scripts/requirements.txt && playwright install chromium
python scripts/check_overflow.py http://localhost:5173
python scripts/check_overflow.py page.html --widths 320,375,414 --screenshots overflow-shots/
```

It only reads the page. It reports a missing viewport tag, a page wider than the screen, the outermost elements that run past either edge, and boxes that silently clip their content. It skips content inside scroll boxes and intentional ellipsis. Treat each hit as a question, not a verdict. If the page needs a dev server, start it with `webapp-testing`'s `scripts/with_server.py`.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It looks fine on my screen." | Your screen is several times wider than a phone. Check at 375px. |
| "`overflow-x: hidden` on the body fixes it." | It hides the scrollbar and the content with it. A clipped button can't be tapped. Fix the element that is too wide. |
| "The names are always short." | Length is set by whoever enters the data. A URL or a model's answer has no upper limit. |
| "I'll add a media query for mobile." | A breakpoint doesn't make a flex item shrink or a word break. Fix the defaults first. |
| "`width: 100%` is enough." | Padding adds to it without `border-box`, and `min-width: auto` still wins inside flex. |
| "`word-break: break-all` everywhere is safest." | It splits ordinary words mid-letter. `overflow-wrap: anywhere` breaks only when it has to. |

## Red Flags

- `overflow-x: hidden` on `html` or `body` added as a fix
- `white-space: nowrap` on containers that hold data or buttons
- Fixed pixel widths on cards, inputs, or dialogs
- A flex child holding text with no `min-width: 0`, or long text in a plain `1fr` grid column
- `100vw` used for widths
- Tables or `pre` blocks with no scroll container
- A layout checked only with short placeholder text, or only on a desktop
- No viewport tag, or one that disables zoom

## Verification

- [ ] Viewport tag present, zoom not disabled
- [ ] `border-box` and media `max-width` rules in place
- [ ] Flex and grid children that hold text can shrink
- [ ] Text of unknown length can break, or truncates on purpose with the full text reachable
- [ ] Action rows wrap; no fixed width is wider than a phone
- [ ] Wide tables and code scroll in their own box, not the page
- [ ] Page checked at 320 and 375px with worst-case content; `scripts/check_overflow.py` run and every hit reviewed
