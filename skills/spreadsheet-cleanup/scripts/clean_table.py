#!/usr/bin/env python3
"""
Profile and clean a messy CSV or Excel table, without touching the original.

Writes:
  <out>                 the cleaned table (same format as the input unless --out says otherwise)
  <out stem>_changes.md a report of every change made and every issue left for a human

Cleaning it does (each can be turned off):
  - trims whitespace and collapses repeated spaces in every cell and header
  - drops rows and columns that are completely empty
  - removes exact duplicate rows (reports near-duplicates that differ only by case/spacing)
  - converts date columns to ISO YYYY-MM-DD when nearly every value parses
  - converts money/number columns ("$1,234.50", "(12.00)") to plain numbers when nearly every value parses

It never converts a column where values have leading zeros (ZIP codes, IDs) or
digit strings longer than 15 characters, and it leaves any column alone when
too many values fail to parse, listing them in the report instead.

Usage:
  clean_table.py input.csv                  # writes input_clean.csv + input_clean_changes.md
  clean_table.py input.xlsx --sheet Loads   # pick a sheet (default: first)
  clean_table.py input.csv --profile        # report only, write no cleaned file
  clean_table.py input.csv --dayfirst       # read 03/04/2026 as 3 April (default: March 4)
"""

import argparse
import csv
import re
import sys
from pathlib import Path

import pandas as pd

PARSE_THRESHOLD = 0.9  # share of non-empty values that must parse before a column is converted
MONEY_RE = re.compile(r"^\(?-?\$?\s*-?\d{1,3}(,\d{3})*(\.\d+)?\)?$|^\(?-?\$?\s*-?\d+(\.\d+)?\)?$")
DATE_HINT_RE = re.compile(r"\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}|[A-Za-z]{3,9}\.? \d{1,2},? \d{4}|\d{1,2} [A-Za-z]{3,9} \d{4}")


def norm_space(value):
    if not isinstance(value, str):
        return value
    return re.sub(r"\s+", " ", value).strip()


def detect_delimiter(path, encoding):
    with open(path, encoding=encoding, newline="") as f:
        sample = f.read(64 * 1024)
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return "\t" if path.suffix.lower() == ".tsv" else ","


def read_table(path, sheet):
    """Return (dataframe, malformed_rows, delimiter). Malformed rows are set aside, not guessed at."""
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(path, sheet_name=sheet if sheet is not None else 0, dtype=str, keep_default_na=False)
        return df.fillna(""), [], None
    if suffix in (".csv", ".tsv", ".txt"):
        for enc in ("utf-8-sig", "cp1252", "latin-1"):
            bad = []
            try:
                sep = detect_delimiter(path, enc)
                df = pd.read_csv(path, dtype=str, keep_default_na=False, sep=sep, engine="python",
                                 encoding=enc, on_bad_lines=lambda line: bad.append(line) or None)
                return df.fillna(""), bad, sep
            except UnicodeDecodeError:
                continue
    sys.exit(f"Unsupported file type: {suffix}")


def write_table(df, path, sep):
    if path.suffix.lower() in (".xlsx", ".xlsm", ".xls"):
        df.to_excel(path.with_suffix(".xlsx"), index=False)
        return path.with_suffix(".xlsx")
    df.to_csv(path, index=False, sep=sep or ("\t" if path.suffix.lower() == ".tsv" else ","))
    return path


def try_money(series):
    """Return (converted series, failures) if the column looks numeric, else None."""
    values = series[series != ""]
    if values.empty:
        return None
    if values.str.match(r"^0\d").any() or values.str.replace(r"\D", "", regex=True).str.len().gt(15).any():
        return None  # leading zeros or very long digit strings: IDs, ZIPs, account-like numbers
    ok = values.str.match(MONEY_RE)
    if ok.mean() < PARSE_THRESHOLD or ok.mean() == 0:
        return None
    if not values[ok].str.contains(r"[$,()]|\.\d", regex=True).any():
        return None  # plain whole numbers are already clean; leave them as text

    def convert(v):
        if v == "" or not MONEY_RE.match(v):
            return v
        negative = v.startswith("(") and v.endswith(")") or "-" in v
        number = float(re.sub(r"[^\d.]", "", v))
        number = -number if negative else number
        return int(number) if number.is_integer() and "." not in v else number

    failures = values[~ok].unique().tolist()
    return series.map(convert), failures


def try_dates(series, dayfirst):
    values = series[series != ""]
    if values.empty or values.str.match(MONEY_RE).mean() > 0.5:
        return None
    if values.str.contains(DATE_HINT_RE).mean() < PARSE_THRESHOLD:
        return None
    parsed = pd.to_datetime(values, errors="coerce", dayfirst=dayfirst, format="mixed")
    ok = parsed.notna()
    if ok.mean() < PARSE_THRESHOLD:
        return None
    has_time = (parsed[ok].dt.hour.ne(0) | parsed[ok].dt.minute.ne(0)).any()
    fmt = "%Y-%m-%d %H:%M" if has_time else "%Y-%m-%d"
    out = series.copy()
    out.loc[parsed[ok].index] = parsed[ok].dt.strftime(fmt)
    ambiguous = values[ok].str.match(r"^(0?[1-9]|1[0-2])[-/.](0?[1-9]|1[0-2])[-/.]\d{2,4}").sum()
    return out, values[~ok].unique().tolist(), int(ambiguous)


def main():
    ap = argparse.ArgumentParser(description="Profile and clean a messy CSV/Excel table.")
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, help="Output path (default: <input>_clean.<ext>)")
    ap.add_argument("--sheet", help="Excel sheet name (default: first sheet)")
    ap.add_argument("--profile", action="store_true", help="Report only; do not write a cleaned file")
    ap.add_argument("--dayfirst", action="store_true", help="Parse ambiguous dates as day/month")
    ap.add_argument("--keep-duplicates", action="store_true")
    ap.add_argument("--no-dates", action="store_true")
    ap.add_argument("--no-numbers", action="store_true")
    args = ap.parse_args()

    if not args.input.exists():
        sys.exit(f"Not found: {args.input}")
    df, malformed, sep = read_table(args.input, args.sheet)
    rows_in, cols_in = df.shape
    changes, issues = [], []
    if malformed:
        rows_in += len(malformed)
        issues.append(f"{len(malformed)} row(s) had the wrong number of fields (usually an unquoted comma) and were "
                      f"set aside, not included in the output. Fix them by hand: "
                      + "; ".join("`" + ",".join(r) + "`" for r in malformed[:10]))

    # Headers
    new_cols, seen = [], {}
    for i, c in enumerate(df.columns):
        name = norm_space(str(c))
        if name == "" or name.startswith("Unnamed:"):
            name = f"column_{i + 1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 1
        new_cols.append(name)
    renamed = [(o, n) for o, n in zip(df.columns, new_cols) if str(o) != n]
    df.columns = new_cols
    if renamed:
        changes.append(f"Renamed {len(renamed)} header(s): " + "; ".join(f"`{o}` → `{n}`" for o, n in renamed[:10]))

    # Whitespace
    before = df.copy()
    df = df.apply(lambda s: s.map(norm_space))
    touched = int((before != df).sum().sum())
    if touched:
        changes.append(f"Trimmed or collapsed whitespace in {touched} cell(s)")

    # Empty rows / columns
    empty_cols = [c for c in df.columns if len(df) and (df[c] == "").all()]
    if empty_cols:
        df = df.drop(columns=empty_cols)
        changes.append(f"Dropped {len(empty_cols)} empty column(s): " + ", ".join(f"`{c}`" for c in empty_cols))
    empty_rows = (df == "").all(axis=1)
    if empty_rows.any():
        changes.append(f"Dropped {int(empty_rows.sum())} completely empty row(s)")
        df = df[~empty_rows]

    # Duplicates
    dupes = df.duplicated()
    if dupes.any():
        if args.keep_duplicates:
            issues.append(f"{int(dupes.sum())} exact duplicate row(s) kept because of --keep-duplicates")
        else:
            changes.append(f"Removed {int(dupes.sum())} exact duplicate row(s) (first copy kept)")
            df = df[~dupes]
    folded = df.apply(lambda s: s.str.lower())
    near = folded.duplicated(keep=False) & ~df.duplicated(keep=False)
    if near.any():
        issues.append(f"{int(near.sum())} row(s) are duplicates except for capitalization. Not removed; review them. "
                      f"Around data rows: {', '.join(str(i + 2) for i in df.index[near][:20])}")

    # Type conversion
    decimals = {}  # numeric column -> decimal places to write
    for col in df.columns:
        if not args.no_dates:
            result = try_dates(df[col], args.dayfirst)
            if result:
                df[col], failed, ambiguous = result
                changes.append(f"`{col}`: converted dates to ISO format")
                if failed:
                    issues.append(f"`{col}`: {len(failed)} value(s) are not dates and were left as-is: {failed[:10]}")
                if ambiguous:
                    order = "day/month" if args.dayfirst else "month/day"
                    issues.append(f"`{col}`: {ambiguous} date(s) like 03/04 could be read either way; read as {order}. "
                                  f"Rerun with{'out' if args.dayfirst else ''} --dayfirst if that's wrong.")
                continue
        if not args.no_numbers:
            result = try_money(df[col])
            if result:
                df[col], failed = result
                decimals[col] = 2 if df[col].map(lambda x: isinstance(x, float)).any() else 0  # money → 2 places
                changes.append(f"`{col}`: converted to numbers (removed $, commas; parentheses → negative)")
                if failed:
                    issues.append(f"`{col}`: {len(failed)} value(s) are not numbers and were left as-is: {failed[:10]}")
                continue
        filled = df[col][df[col] != ""]
        if not filled.empty and not args.no_dates and filled.str.contains(DATE_HINT_RE).mean() >= 0.5:
            bad = filled[~filled.str.contains(DATE_HINT_RE)].unique().tolist()
            issues.append(f"`{col}` looks like dates but was left unconverted because these values aren't dates: "
                          f"{bad[:10]}. Fix or blank them, then rerun.")
        elif not filled.empty and not args.no_numbers and filled.str.contains(r"\$").mean() >= 0.5:
            bad = filled[~filled.str.match(MONEY_RE)].unique().tolist()
            issues.append(f"`{col}` looks like money but was left unconverted because these values aren't numbers: "
                          f"{bad[:10]}. Fix or blank them, then rerun.")

    # Profile
    profile = ["| Column | Filled | Distinct | Example |", "|---|---|---|---|"]
    for col in df.columns:
        s = df[col].astype(str)
        filled = int((s != "").sum())
        example = next((v for v in s if v != ""), "")
        profile.append(f"| {col} | {filled}/{len(s)} | {s[s != ''].nunique()} | {example[:40]} |")
        if 0 < filled < len(s) * 0.5:
            issues.append(f"`{col}` is less than half filled ({filled}/{len(s)})")

    out = args.out or args.input.with_name(f"{args.input.stem}_clean{args.input.suffix}")
    if not args.profile:
        if out.suffix.lower() not in (".xlsx", ".xlsm", ".xls"):
            for col, d in decimals.items():
                df[col] = df[col].map(lambda x, d=d: f"{x:.{d}f}" if isinstance(x, (int, float)) else x)
        out = write_table(df, out, sep)
    report_path = out.with_name(f"{out.stem}_changes.md")
    report = [
        f"# Cleanup report: {args.input.name}",
        "",
        f"- Input: {rows_in} rows × {cols_in} columns",
        f"- Output: {len(df)} rows × {len(df.columns)} columns" + (" (profile only, nothing written)" if args.profile else f" → `{out.name}`"),
        "",
        "## Changes made" if not args.profile else "## Changes that would be made",
        *(f"- {c}" for c in changes or ["None"]),
        "",
        "## Needs a human",
        *(f"- {i}" for i in issues or ["Nothing flagged"]),
        "",
        "## Column profile",
        *profile,
        "",
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
