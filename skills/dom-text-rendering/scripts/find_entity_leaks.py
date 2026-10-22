#!/usr/bin/env python3
"""Find HTML entities that will render as literal text, and risky HTML sinks.

Scans JavaScript/TypeScript (and Vue/Svelte) source for two patterns:

  entity-in-string  An HTML entity such as &#10003; or &amp; inside a JS string
                    literal. Text APIs (textContent, JSX {expressions}, most
                    framework bindings) show these as literal characters.
  dynamic-html      An HTML-parsing sink (innerHTML, outerHTML,
                    insertAdjacentHTML, document.write, dangerouslySetInnerHTML,
                    v-html) that receives a template or concatenated value
                    instead of a fixed string. Check that the value is trusted
                    markup or sanitized.

Hits are prompts for review, not verdicts. The scanner is line-based and only
reads files; it never modifies anything.

Usage:
  python find_entity_leaks.py PATH [PATH ...]
  python find_entity_leaks.py src/ --ext .js .ts

Exit status: 0 when nothing is found, 1 when there are hits, 2 on bad input.
"""

import argparse
import os
import re
import sys

DEFAULT_EXTS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "out", ".next", "coverage", "vendor"}

ENTITY = r"&(?:#\d{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z][A-Za-z0-9]{1,31});"
STRING_LITERAL = re.compile(r"""(['"`])((?:\\.|(?!\1).)*?)\1""")
ENTITY_RE = re.compile(ENTITY)

HTML_SINK = re.compile(
    r"(?:\.(?:innerHTML|outerHTML)\s*\+?=\s*(?P<rhs>.*)"
    r"|insertAdjacentHTML\s*\(\s*['\"][^'\"]*['\"]\s*,\s*(?P<arg>.*)"
    r"|document\.write(?:ln)?\s*\((?P<warg>.*)"
    r"|dangerouslySetInnerHTML\s*=\s*\{\{\s*__html\s*:\s*(?P<react>.*)"
    r"|v-html\s*=\s*\"(?P<vue>[^\"]*)\")"
)
PLAIN_STRING_ONLY = re.compile(r"""^\s*(['"])(?:\\.|(?!\1).)*\1\s*[;,)}]*\s*(?://.*)?$""")
TEMPLATE_NO_INTERP = re.compile(r"^\s*`[^`$]*`\s*[;,)}]*\s*(?://.*)?$")


def is_dynamic(value):
    """True when a sink's argument is anything other than one fixed string."""
    if value is None:
        return False
    value = value.strip()
    if not value or value in {"''", '""', "``"}:
        return False
    if PLAIN_STRING_ONLY.match(value) or TEMPLATE_NO_INTERP.match(value):
        return False
    return True


def scan_line(line):
    hits = []
    stripped = line.lstrip()
    if stripped.startswith("//") or stripped.startswith("*"):
        return hits

    sink = HTML_SINK.search(line)
    sink_is_html = sink is not None

    for match in STRING_LITERAL.finditer(line):
        body = match.group(2)
        entity = ENTITY_RE.search(body)
        if entity and not sink_is_html:
            hits.append((match.start() + 1, "entity-in-string", entity.group(0)))

    if sink:
        value = next((v for v in sink.groupdict().values() if v is not None), None)
        if is_dynamic(value):
            hits.append((sink.start() + 1, "dynamic-html", value.strip()[:60]))
    return hits


def iter_files(paths, exts):
    for path in paths:
        if os.path.isfile(path):
            yield path
            continue
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in sorted(files):
                if name.endswith(".min.js"):
                    continue
                if os.path.splitext(name)[1] in exts:
                    yield os.path.join(root, name)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("paths", nargs="+", help="files or folders to scan")
    parser.add_argument("--ext", nargs="+", help="file extensions to include")
    args = parser.parse_args()

    exts = set(args.ext) if args.ext else DEFAULT_EXTS
    missing = [p for p in args.paths if not os.path.exists(p)]
    if missing:
        print(f"Not found: {', '.join(missing)}", file=sys.stderr)
        return 2

    total = 0
    for path in iter_files(args.paths, exts):
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                for number, line in enumerate(handle, 1):
                    for col, kind, detail in scan_line(line):
                        print(f"{path}:{number}:{col}  {kind}  {detail}")
                        total += 1
        except OSError as err:
            print(f"Skipped {path}: {err}", file=sys.stderr)

    print(f"\n{total} hit(s). Review each one; see SKILL.md Steps 2-4.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
