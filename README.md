# QA Results Validator

**Independent QA Data Quality Demo**

A small Python script for checking a single-run test-results export before using it in a QA summary. The sample belongs to a fictional DemoShop workflow and deliberately contains errors. No client data is included.

## Run

Requires Python 3.9 or later. No packages need to be installed. From this directory:

```bash
python qa_validator.py
```

On Windows, `py qa_validator.py` is also suitable if the Python launcher is installed.

To select another CSV or output path:

```bash
python qa_validator.py another_run.csv --output review.txt
```

The report is printed and written to `qa_validation_report.txt`. That generated report is ignored by Git; `example_report.txt` is the committed example. Exit codes: 0 = no validation findings, 1 = findings to resolve, 2 = input/output error. The included fixture intentionally returns 1.

## Input contract

One record per test ID in one run. Required columns are `Test Case ID`, `Title`, `Status`, `Actual Result`, `Bug ID`. ID, Title and Status must be nonblank on every row. Status values are exactly `Passed`, `Failed`, `Blocked`, `Not Run`. A failed row also needs Actual Result. Bug ID may be blank. UTF-8 and UTF-8 with BOM are accepted. Cell whitespace is stripped; status spelling is not silently corrected.

The script checks missing values, repeated IDs, unknown statuses, Passed with a Bug ID, and Failed without Actual Result. Missing/duplicate headers stop processing; malformed row widths are reported. Extra named columns are ignored. IDs are compared case-sensitively. Record numbers count parsed CSV records including the header, not physical lines when a quoted cell spans lines.

## Workflow

Export one run, run the checker, review each finding, correct the source records, and export again. The script never edits the input. It does not decide which duplicate to keep. A multi-run export needs a composite run/execution key before this checker is appropriate.

This input uses Bug ID to mean a defect associated with the current failed execution. A historical resolved bug belongs in a separate field. The Airtable demo preserves such history through a dedicated Retest Test Case link.

## Summary logic

Counts use raw rows, including rows with findings. Pass rate = Passed / (Passed + Failed). Blocked, Not Run and invalid statuses are excluded from that denominator. Zero denominator produces N/A. Any finding marks the summary provisional; it must not be treated as a clean project KPI.

## Actual example output

```text
QA RESULTS VALIDATION
Input: test_results.csv
Total test rows: 15
Unique nonblank IDs: 13
Blocked: 2
Failed: 5
Not Run: 1
Passed: 6
Invalid/blank status: 1
Pass rate (Passed / (Passed + Failed)): 54.5%
Counts are raw rows; duplicates are not silently removed.
PROVISIONAL: fix validation issues before reporting.
Issues: 6
Record 10: duplicate TC-001 (first: 2)
Record 11: missing Title
Record 12: missing Test Case ID
Record 13: invalid Status 'Pass'
Record 14: Passed with Bug ID
Record 15: Failed without Actual Result
```

## Learning objective

Use CSV parsing, dictionaries, sets, counting and simple conditional checks to turn a repetitive review into a readable report. The script reports inconsistencies rather than silently modifying source data.
