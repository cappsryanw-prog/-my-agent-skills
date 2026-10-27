---
name: data-storyteller
description: Analyzes a CSV, Excel, or JSON dataset and turns it into a short, plain-English story (what's happening, what changed, what looks wrong, and what to do next), backed by scripts for profiling, data-quality audits, outliers, pivots, comparisons, time series, statistics, budgets, surveys, A/B tests, and ROI. Use when the user shares a data export and asks "what does this tell us", "analyze this", "summarize these numbers", "compare this month to last", "anything weird in here", "build me a report", or needs numbers for a meeting, a pitch, or a manager. Use it even when the user doesn't say "analysis".
---

# Data Storyteller

## Overview

People don't need every statistic in a file. They need the three or four things that matter, stated with numbers, plus a warning when the data can't support a strong claim. The usual failures run in both directions. One is a wall of charts that answers nothing. The other is a confident headline built on a column that was half blank, a duplicate-heavy export, or a single outlier.

This skill works in that order on purpose. It profiles and audits the data first, runs only the analysis the question needs, and then writes the finding in plain words with the evidence and its limits. The scripts handle the arithmetic, so the numbers come from code, not from estimates.

## When to Use

- "What does this data tell us?", "summarize this export", "build me a report from this"
- Numbers for a decision or a pitch: revenue by customer, week-over-week change, top accounts
- "Anything weird in here?" (outliers, gaps, duplicates)
- Comparing two versions of a dataset, two periods, or two groups
- Trends and seasonality over time, budgets against actuals, survey results, A/B tests, ROI

**When NOT to use:**

- The file needs cleaning before anything else (mixed dates, money stored as text, junk rows). Run `spreadsheet-cleanup` first, then come back.
- The user only wants a single number or one lookup. Answer it directly.
- The data is someone's private information that the user hasn't said they're allowed to analyze.

## The Process

### Step 1: Get the question before touching the data

Write the user's actual question in one sentence. "Analyze this" usually means something more specific, such as "which accounts are growing" or "is this cost going up." If you can't tell, ask one question, or state the reading you're taking. Every later step serves that sentence.

### Step 2: Profile and audit

```bash
pip install -r scripts/requirements.txt
python scripts/data_quality_auditor.py --input <file>
```

Read the quality score and the issues list. Look for missing values in the columns that answer the question, duplicates, dates stored as text, and outliers. Fix what you can in a copy, and note what you can't. **Never edit the user's original file.** Every script reads its input and writes to a separate output.

Non-CSV inputs (Numbers, XML, YAML) go through `data_converter.py` first. For Apple `.numbers` files, use the `numbers-parser` package (`pip install numbers-parser`).

### Step 3: Run only what the question needs

| Question | Script |
|---|---|
| Full narrative report (HTML, PDF, or JSON) | `data_storyteller.py <file> -o report.html -s business` |
| Totals by group (customer, month, lane) | `pivot_table_generator.py --data <file> --rows <col> --columns <col> --values <col> --agg sum -o pivot.csv` |
| What's unusual | `outlier_detective.py --input <file> --column <col>` |
| What moves together | `correlation_explorer.py --input <file>` |
| Trend and seasonality, simple forecast | `ts_decomposer.py --input <file> --date <col> --value <col> --period 7` |
| Old vs. new file, or this period vs. last | `dataset_comparer.py --old a.csv --new b.csv --key <id col>` |
| Is the difference real | `statistical_analyzer.py --data <file> --test t-test --group <col> --value <col> -o out.json` |
| Spending against budget | `budget_analyzer.py --input <file> --date <col> --amount <col> --category-col <col>` |
| Survey responses | `survey_analyzer.py --data <file> --likert <col> -o out.json` |
| Experiment result or sample size | `ab_test_calc.py` |
| Payback, break-even, ROI | `roi_calculator.py` |

Run each script with `-h` for every option. For a one-off cut that no script covers, write a short pandas script. Still compute everything in code.

### Step 4: Check the numbers

Before writing the story, confirm the totals add up to the source, that row counts match, and that date ranges are what you think they are. Watch for a partial current week or month, which makes the latest period look like a drop. When the data includes future or scheduled rows, cut it off at today.

### Step 5: Write the story

Keep it to one screen, with the finding first:

```
**Bottom line:** one sentence with the key number.

**What the data shows**
- 3–5 findings, each with a number and the comparison that makes it meaningful (vs. last period, vs. the average, share of the total)

**Watch out for:** data limits that change how far to trust it (missing data, short history, costs the export doesn't include)

**Next step:** one action the findings point to
```

Add a table only if it has 6 rows or fewer. Use a chart for anything over time or with more items, and follow a charting skill for style if one is available. Put the method detail after the story, or leave it out.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll run every script so nothing is missed." | That buries the answer. Run what the question needs. |
| "The data looks clean, so I'll skip the audit." | Blank columns and duplicates don't show at a glance. The audit takes seconds. |
| "These two move together, so one causes the other." | Correlation isn't cause. Say "moves with", not "drives". |
| "The last bar dropped, so things are getting worse." | Check whether it's a partial period first. |
| "I can estimate the total from what I've seen." | Run it in code. Estimated numbers are how reports go wrong. |
| "More charts look more thorough." | One chart that answers the question beats six that don't. |

## Red Flags

- A headline number that no script or code produced
- Findings stated without a comparison (is $14k a week good or bad?)
- Causal language ("because", "drives") based only on correlation
- The original file modified, or outputs written over the input
- A data-quality issue found in the audit but left out of the story
- A report longer than one screen before the first finding

## Verification

- [ ] The user's question is written in one sentence, and the story answers it
- [ ] The audit ran, and its issues are fixed or named in "Watch out for"
- [ ] Every number comes from code, and totals match the source
- [ ] Partial periods and future rows are handled
- [ ] The original file is unchanged
- [ ] The story fits one screen, with the finding first
