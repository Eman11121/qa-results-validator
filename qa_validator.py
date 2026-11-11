"""Check a single test-run CSV export using only the Python standard library."""
import argparse
import csv
from collections import Counter
from pathlib import Path

COLUMNS = ("Test Case ID", "Title", "Status", "Actual Result", "Bug ID")
REQUIRED = ("Test Case ID", "Title", "Status")
STATUSES = {"Passed", "Failed", "Blocked", "Not Run"}


def validate(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise ValueError("Duplicate column headers")
        missing = set(COLUMNS) - set(headers)
        if missing:
            raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
        rows = list(reader)
    issues, counts, seen = [], Counter(), {}
    for number, raw in enumerate(rows, start=2):
        # Record numbers include the header; multiline CSV cells may span lines.
        if None in raw or any(value is None for value in raw.values()):
            issues.append(f"Record {number}: wrong number of CSV fields")
        row = {key: (raw.get(key) or "").strip() for key in COLUMNS}
        for key in REQUIRED:
            if not row[key]:
                issues.append(f"Record {number}: missing {key}")
        test_id, status = row["Test Case ID"], row["Status"]
        if test_id:
            if test_id in seen:
                issues.append(f"Record {number}: duplicate {test_id} (first: {seen[test_id]})")
            else:
                seen[test_id] = number
        if status not in STATUSES:
            issues.append(f"Record {number}: invalid Status {status!r}")
        counts[status] += 1
        if status == "Passed" and row["Bug ID"]:
            issues.append(f"Record {number}: Passed with Bug ID")
        if status == "Failed" and not row["Actual Result"]:
            issues.append(f"Record {number}: Failed without Actual Result")
    decided = counts["Passed"] + counts["Failed"]
    rate = f"{counts['Passed'] / decided:.1%}" if decided else "N/A"
    report = ["QA RESULTS VALIDATION", f"Input: {path.name}",
              f"Total test rows: {len(rows)}", f"Unique nonblank IDs: {len(seen)}"]
    report += [f"{status}: {counts[status]}" for status in sorted(STATUSES)]
    report += [f"Invalid/blank status: {sum(v for k, v in counts.items() if k not in STATUSES)}",
               f"Pass rate (Passed / (Passed + Failed)): {rate}",
               "Counts are raw rows; duplicates are not silently removed.",
               "PROVISIONAL: fix validation issues before reporting." if issues else "Validation: OK",
               f"Issues: {len(issues)}", *issues]
    return "\n".join(report) + "\n", bool(issues)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, default=Path("test_results.csv"))
    parser.add_argument("--output", type=Path, default=Path("qa_validation_report.txt"))
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Output must not overwrite input")
        report, invalid = validate(args.input)
        args.output.write_text(report, encoding="utf-8")
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        parser.exit(2, f"Input/output error: {error}\n")
    print(report, end="")
    return int(invalid)


if __name__ == "__main__":
    raise SystemExit(main())
