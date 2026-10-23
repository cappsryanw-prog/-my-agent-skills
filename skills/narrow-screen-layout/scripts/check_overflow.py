#!/usr/bin/env python3
"""Check a web page for content that runs off a phone-width screen.

Loads a URL or local HTML file in headless Chromium at one or more phone
widths and reports:

  no-viewport     The page has no <meta name="viewport">, so phones lay it out
                  about 980px wide and shrink it.
  page-overflow   The document is wider than the screen (sideways scrolling),
                  or would be if overflow were not hidden on html/body.
  off-screen      The outermost visible elements that extend past the left or
                  right edge. Their descendants are not listed separately.
  clipped         A box with overflow hidden/clip whose content is wider than
                  the box, so part of it is cut off. Intentional ellipsis
                  (text-overflow: ellipsis) is skipped.

Content inside a horizontal scroll container (overflow-x: auto or scroll,
other than html/body) is skipped, because scrolling there is intended.

Hits are prompts for review, not verdicts. The script only reads the page.
The one thing it writes is screenshots, and only into the --screenshots
directory you name, which must be new or empty.

Usage:
  python check_overflow.py http://localhost:5173
  python check_overflow.py page.html --widths 320,375,414
  python check_overflow.py page.html --screenshots overflow-shots/

Exit status: 0 when nothing is found, 1 when there are hits, 2 on bad input
or a page that fails to load.
"""

import argparse
import os
import pathlib
import sys

try:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("check_overflow.py needs Playwright: pip install -r requirements.txt "
             "&& playwright install chromium")

# Runs in the page. Returns plain data only.
PROBE = r"""
() => {
  const vw = document.documentElement.clientWidth;
  const root = document.documentElement, body = document.body;
  const out = { vw, docWidth: root.scrollWidth, offScreen: [], clipped: [] };

  const meta = document.querySelector('meta[name="viewport"]');
  out.hasViewport = !!(meta && /width\s*=\s*device-width/i.test(meta.content || ''));

  const isPageLevel = (el) => el === root || el === body;
  const scrollsX = (cs) => cs.overflowX === 'auto' || cs.overflowX === 'scroll';
  const clipsX = (cs) => cs.overflowX === 'hidden' || cs.overflowX === 'clip';

  // Widest content measured with page-level clipping lifted, so a hidden
  // overflow on html/body is still reported.
  const saved = [root.style.overflowX, body ? body.style.overflowX : ''];
  root.style.overflowX = 'visible';
  if (body) body.style.overflowX = 'visible';
  out.trueDocWidth = root.scrollWidth;
  root.style.overflowX = saved[0];
  if (body) body.style.overflowX = saved[1];
  out.pageClipsX = clipsX(getComputedStyle(root)) || (body && clipsX(getComputedStyle(body)));

  const describe = (el) => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    const cls = (typeof el.className === 'string' ? el.className : '')
      .trim().split(/\s+/).filter(Boolean).slice(0, 3);
    if (cls.length) s += '.' + cls.join('.');
    const text = (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim();
    return { selector: s, text: text.length > 50 ? text.slice(0, 47) + '...' : text };
  };

  const visible = (el, cs, r) =>
    cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 0 && r.height > 0;

  // Skip anything inside an intended horizontal scroll box.
  const inScrollBox = (el) => {
    for (let a = el.parentElement; a && !isPageLevel(a); a = a.parentElement) {
      if (scrollsX(getComputedStyle(a))) return true;
    }
    return false;
  };

  const overflows = new Set();
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    if (!visible(el, cs, r) || inScrollBox(el)) continue;

    if (r.right > vw + 1 || r.left < -1) {
      overflows.add(el);
      if (!overflows.has(el.parentElement)) {
        out.offScreen.push(Object.assign(describe(el), {
          left: Math.round(r.left), right: Math.round(r.right), width: Math.round(r.width) }));
      }
    }

    if (clipsX(cs) && cs.textOverflow !== 'ellipsis' &&
        el.scrollWidth > el.clientWidth + 1 && !isPageLevel(el)) {
      out.clipped.push(Object.assign(describe(el), {
        boxWidth: el.clientWidth, contentWidth: el.scrollWidth }));
    }
  }
  return out;
}
"""


def resolve_target(target):
    if "://" in target:
        return target
    path = pathlib.Path(target)
    if not path.is_file():
        print(f"error: {target} is not a URL or an existing file", file=sys.stderr)
        sys.exit(2)
    return path.resolve().as_uri()


def prepare_shot_dir(path):
    if path is None:
        return None
    d = pathlib.Path(path)
    if d.exists() and (not d.is_dir() or any(d.iterdir())):
        print(f"error: {path} must be a new or empty directory", file=sys.stderr)
        sys.exit(2)
    d.mkdir(parents=True, exist_ok=True)
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("target", help="URL or local HTML file")
    ap.add_argument("--widths", default="320,375",
                    help="comma-separated viewport widths in CSS pixels (default 320,375)")
    ap.add_argument("--height", type=int, default=800, help="viewport height (default 800)")
    ap.add_argument("--screenshots", metavar="DIR",
                    help="save a full-page screenshot per width into this new or empty directory")
    ap.add_argument("--timeout", type=int, default=30, help="page load timeout in seconds")
    args = ap.parse_args()

    try:
        widths = [int(w) for w in args.widths.split(",") if w.strip()]
    except ValueError:
        print("error: --widths must be numbers like 320,375", file=sys.stderr)
        return 2
    url = resolve_target(args.target)
    shots = prepare_shot_dir(args.screenshots)

    hits = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for w in widths:
                ctx = browser.new_context(viewport={"width": w, "height": args.height},
                                          is_mobile=True, has_touch=True, device_scale_factor=2)
                page = ctx.new_page()
                try:
                    page.goto(url, wait_until="networkidle", timeout=args.timeout * 1000)
                except PlaywrightError as e:
                    print(f"error: could not load {url}: {e}", file=sys.stderr)
                    return 2
                res = page.evaluate(PROBE)
                if shots:
                    page.screenshot(path=str(shots / f"width-{w}.png"), full_page=True)
                ctx.close()

                print(f"== {w}px wide (layout width {res['vw']}px)")
                found = []
                if not res["hasViewport"]:
                    found.append("  no-viewport    no <meta name=\"viewport\" content=\"width=device-width, ...\">; "
                                 "phones will shrink a ~980px layout")
                if res["trueDocWidth"] > res["vw"] + 1:
                    note = " (hidden by overflow on html/body; content is cut off)" if res["pageClipsX"] else ""
                    found.append(f"  page-overflow  content is {res['trueDocWidth']}px wide on a "
                                 f"{res['vw']}px screen{note}")
                for o in res["offScreen"]:
                    found.append(f"  off-screen     {o['selector']}  spans {o['left']}..{o['right']}px"
                                 f"  \"{o['text']}\"")
                for c in res["clipped"]:
                    found.append(f"  clipped        {c['selector']}  box {c['boxWidth']}px, content "
                                 f"{c['contentWidth']}px  \"{c['text']}\"")
                print("\n".join(found) if found else "  ok")
                hits += len(found)
        finally:
            browser.close()

    if shots:
        print(f"screenshots: {shots}")
    print(f"{hits} finding(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
