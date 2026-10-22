---
name: spreadsheet-cleanup
description: Cleans messy CSV and Excel exports into a tidy table, fixing whitespace, blank rows, duplicates, mixed date formats, and money stored as text, without touching the original file and with a written report of every change. Use when the user shares an export from a CRM, accounting, TMS, ERP, or survey tool and asks to clean, tidy, dedupe, standardize, or prepare it for analysis, import, or a pivot table.
---

# Spreadsheet Cleanup

## Overview

Exports from business systems are rarely analysis-ready. Headers have stray spaces, totals rows and blank rows are mixed in, dates come in three formats, money is text with dollar signs, and the same record appears twice. Cleaning that by hand is slow, and cleaning it carelessly is worse: a ZIP code loses its leading zero, 03/04 silently becomes April 3, or a "duplicate" that was really two separate shipments gets deleted.

This skill cleans with a script that makes only safe, mechanical fixes, never overwrites the source, and writes down every change plus everything it was **not** sure about, so a person decides those.

## When to Use

- "Clean up this export", "dedupe this list", "fix the dates", "get this ready for a pivot table / import"
- Before analyzing or charting data that came out of another system
- Before importing a file into another system that will reject bad rows

**When NOT to use:**

- The data is already clean and typed. Go straight to the analysis.
- The user wants records merged by judgment (e.g. "Acme Foods" vs "Acme Foods Inc."). Report candidates; let the user decide the rule.

## The Process

### Step 1: Profile first

```bash
pip install -r scripts/requirements.txt
python scripts/clean_table.py <file> --profile
```

`--profile` writes nothing except the report. Read it with the user's goal in mind: what the columns are, how full they are, and what the script would change. For Excel, pass `--sheet <name>` if the data isn't on the first sheet.

Before cleaning, look for things the script deliberately doesn't handle:

- **Title rows or notes above the header.** Delete them in a copy, or tell the user.
- **Totals or subtotal rows.** They will be treated as data. Remove them or flag them.
- **Merged cells or multi-row headers** in Excel. Flatten them first.

### Step 2: Confirm the risky choices

Ask the user only where a wrong guess changes the data:

- **Date order.** If the report shows ambiguous dates like 03/04/2026, confirm month/day (default) or day/month (`--dayfirst`).
- **Duplicates.** Exact duplicate rows are removed by default. If repeated rows can be legitimate (two identical shipments on one day), use `--keep-duplicates`.

### Step 3: Clean

```bash
python scripts/clean_table.py <file> [--dayfirst] [--keep-duplicates] [--out cleaned.csv]
```

The output defaults to `<name>_clean.<ext>` next to the input, plus `<name>_clean_changes.md`. The original file is never modified.

What the script does:

| Fix | Safeguard |
|---|---|
| Trims and collapses whitespace in cells and headers; names blank headers, de-duplicates header names | — |
| Drops fully empty rows and columns | Only if every cell is empty |
| Removes exact duplicate rows | Rows differing only by capitalization are reported, not removed |
| Dates → ISO `YYYY-MM-DD` | Only if ≥90% of values parse; ambiguous day/month counts are reported |
| Money/numbers as text → numbers (`$1,234.50` → `1234.50`, `(12.00)` → `-12.00`) | Never touches columns with leading zeros (ZIPs, IDs) or digit strings over 15 characters |
| Rows with the wrong number of fields (CSV) | Set aside and listed, never guessed at |

A column that *looks* like dates or money but has values that don't parse (e.g. "TBD") is left unchanged, and the report lists the bad values.

### Step 4: Resolve the "Needs a human" list

Go through each flagged item with the user. Fix the source values or decide a rule, then rerun the script on the corrected copy. Don't hand-edit the cleaned output, since a rerun would lose those edits.

### Step 5: Report

Tell the user, briefly:

- Rows and columns in → out
- The main changes (from the report)
- Anything still unresolved
- Where the cleaned file and the report are

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll just fix it in pandas inline." | Ad-hoc cleaning drops leading zeros and flips dates without anyone noticing. The script's guards exist for exactly those cases. |
| "Those rows look like duplicates, delete them." | Identical-looking rows can be separate real events. Exact duplicates only, and say how many. |
| "The dates are obviously month-first." | Not if the file came from a non-US system. Check the ambiguous count and ask. |
| "I'll overwrite the original to keep things simple." | Then there's no way to check or redo the cleanup. Always write a new file. |
| "A few bad values don't matter, coerce them to blank." | Blanking hides data problems. Leave them and list them. |

## Red Flags

- Writing over the user's original file
- A ZIP code, account number, or ID column that turned into numbers
- Dates converted without checking the day/month question
- Rows silently dropped without a count in the report
- Totals rows left in data that will be summed

## Verification

- [ ] Profile run and read before cleaning
- [ ] Title/notes/totals rows handled or flagged
- [ ] Date order and duplicate policy confirmed when the report flagged them
- [ ] Original file unchanged; cleaned file and change report written
- [ ] Every "Needs a human" item resolved or passed to the user
- [ ] Row counts in → out reported, with reasons for any difference
