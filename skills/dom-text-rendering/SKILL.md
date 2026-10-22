---
name: dom-text-rendering
description: Puts text, symbols, and data into a web page so it renders as intended and stays safe, choosing correctly between textContent, innerHTML, JSX, and template strings. Use when writing or fixing frontend code that sets text in the DOM, shows icons or symbols like ✓ ✗ → or ©, renders API, AI, or user-supplied text, or when a page shows literal codes such as &#10003;, &amp;, &nbsp;, or ✓ instead of the character.
---

# DOM Text Rendering

## Overview

Browsers have two different ways to receive text, and mixing them up causes a whole family of bugs. HTML parsing (`innerHTML`, HTML files, server templates) decodes entities like `&#10003;` into ✓. Text APIs (`textContent`, `innerText`, `createTextNode`, JSX text expressions, most framework bindings) put the string on screen exactly as written, so `&#10003;` shows up as eight literal characters.

The tempting fix, switching to `innerHTML` so the entity decodes, trades a cosmetic bug for a security one. If any part of that string ever comes from an API, a model, a URL, or a user, it can now inject markup and script. This skill picks the right channel up front: literal characters in code, text APIs for data, and HTML parsing only for markup you wrote and trust.

## When to Use

- Writing code that sets a button label, status badge, table cell, or message in the DOM
- Showing symbols or icons as text (✓ ✗ ⚠ → • © …)
- Rendering text that came from an API, database, AI model, file, or user input
- A page displays `&#10003;`, `&amp;`, `&nbsp;`, `&lt;b&gt;`, or `✓` where a character or formatting should be
- Reviewing a diff that switches `textContent` to `innerHTML`

**When NOT to use:**

- Static HTML files with no script. Entities there decode normally; leave them.
- Rich text that must keep formatting from an untrusted source (Markdown, comments). Use a vetted sanitizer such as DOMPurify and that library's guidance instead.
- Server-side template escaping rules for a specific framework. Follow the framework's docs.

## The Process

### Step 1: Identify where the string comes from

For each piece of text you're placing, decide which it is:

- **Fixed text you wrote** (a label, a symbol)
- **Data** (anything from fetch, a database, a model, `location`, form input, localStorage), even if it "always" looks safe today
- **Markup you wrote** (a fixed fragment with tags, such as `<strong>`)

Mixed strings, like `"✓ " + repo.name`, count as data.

### Step 2: Write fixed symbols as literal characters

In JavaScript, write the character itself: `'✓ Analyzed'`. Files are UTF-8, so this works everywhere a modern build runs. If a literal is impractical (an ambiguous or invisible character), use a JavaScript escape, `'✓ Analyzed'`, which the JS engine decodes before the DOM ever sees it.

HTML entities (`&#10003;`, `&check;`) belong only in HTML that the browser parses. They are not a JavaScript string escape.

Watch for the same mistake in data: JSON or CSV that contains `&amp;` or `&#39;` was HTML-encoded somewhere upstream. Decode it once at the boundary (or fix the producer), not by rendering it as HTML.

### Step 3: Put data in with a text API

Use `textContent` (or `createTextNode`, or the framework's normal text binding: `{value}` in JSX, `{{ value }}` in Vue). It cannot run markup, so it is safe for anything.

When you need structure around data, build elements and fill each one's text:

```js
const badge = document.createElement('span');
badge.className = 'status';
badge.textContent = `✓ ${repo.name}`;
card.append(badge);
```

Avoid `innerText` for writing; it is slower and depends on layout and CSS. `textContent` is the default.

### Step 4: Use HTML parsing only for trusted markup

`innerHTML`, `insertAdjacentHTML`, `outerHTML`, `document.write`, React's `dangerouslySetInnerHTML`, and Vue's `v-html` are acceptable only when the whole string is markup you wrote in code. If data must go inside markup, escape it first or, better, build elements as in Step 3. If untrusted rich text is a real requirement, sanitize it with a maintained library and say so in the code.

### Step 5: Check the rendered result

Load the page and look at the actual text, including on a phone-width viewport. Then search the code you touched for entities sitting in script strings:

```bash
python scripts/find_entity_leaks.py src/
```

The script is read-only. It flags HTML entities inside JS/TS strings that feed text APIs or JSX, and HTML-parsing sinks that receive a template or concatenated string. Treat each hit as a question, not a verdict; review it and fix or dismiss it.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Switching to innerHTML makes the ✓ show up." | It also lets any data in that string inject script. Write the literal ✓ and keep textContent. |
| "This text comes from my own API, so it's safe." | APIs return what users, models, and third parties put in them. Treat it as data. |
| "Entities are the safe, portable way to write symbols." | Only in HTML. In a JS string, an entity is just text. UTF-8 literals or `\u` escapes are portable. |
| "It renders fine on my screen." | Check the real page, every place the string appears, and data with `<`, `&`, and quotes in it. |
| "I'll unescape it with a quick regex." | Hand-rolled decoders miss cases. Fix the producer, or decode once with a real parser at the boundary. |

## Red Flags

- `&...;` entities inside a JavaScript or TypeScript string literal
- A fix that changes `textContent` to `innerHTML` to make a character appear
- `innerHTML` built with `+` or `${}` that includes anything from fetch, a model, the URL, or input
- `dangerouslySetInnerHTML` or `v-html` on data with no sanitizer
- Double-encoded output such as `&amp;amp;` or `&amp;#39;`
- Text verified only in the source code, never on the rendered page

## Verification

- [ ] Every string placed in the DOM was classified as fixed text, data, or trusted markup
- [ ] Symbols are literal characters or `\u` escapes, not HTML entities, in script code
- [ ] Data goes through textContent or the framework's text binding
- [ ] Any HTML-parsing sink receives only markup written in code, or sanitized output
- [ ] The rendered page was checked and shows the intended characters
- [ ] `scripts/find_entity_leaks.py` run on the touched files, and each hit reviewed
