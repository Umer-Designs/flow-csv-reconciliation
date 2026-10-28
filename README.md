# Flow CSV reconciliation

Validate invoice CSV exports and calculate outstanding balances using the Python standard library.

[Portfolio](https://umer-designs.github.io) · [Browser interface](https://umer-designs.github.io/automation.html)

## Run

Requires Python 3.12+. Processing itself needs no external packages or API credits.

```sh
python flow.py sample.csv --output report.json --state runs.db
# Tests only:
python -m pip install pytest
python -m pytest -q
```

Expected header: `invoice_id,customer,amount,paid`. Inputs are limited to 100 KB and use USD. Currency fields allow up to two decimal places. Invalid amounts, missing identifiers, extra columns, overpayments and duplicate invoice IDs are rejected with source line numbers. Quoted CSV customer names are supported.

## Design

`reconciliation.py` contains the pure parser and reconciliation function. The FastAPI service uses the same file for HTTP execution; the file is kept verbatim in both repositories. `flow.py` adds content-hash-based SQLite report caching and atomic output replacement for command line use.

The report contains accepted rows, rejected rows, integer-cent totals and a deterministic summary. Repeating an identical file returns a cached report. This is file-level caching, not a global invoice database across changing exports.

The browser interface has a local JavaScript preview and a Python-service control. Python mode becomes available only when a deployed service URL is configured. It sends the CSV to `/reconcile`; the HTTP path does not save input CSVs. The Python CLI remains usable offline regardless of hosting availability.

Ten automated tests cover exact decimals, invalid values, duplicate and overpaid rows, file caching, empty files, bad headers and quoted customer names. Scheduling and email delivery are outside the project scope. MIT licensed.
