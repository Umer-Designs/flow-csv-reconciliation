# Flow CSV Reconciliation

Independent portfolio project by Umer Khalid, 2026. All example data is fictional.

## Run

```text
python flow.py sample.csv --output report.json --state runs.db
# Optional test dependency
python -m pip install pytest
python -m pytest -q
```

Requires Python 3.12+. Processing uses the standard library; pytest is needed only for tests.

## Features

Python standard library pipeline. Decimal validation, duplicate rejection, outstanding totals, deterministic summary, content-addressed SQLite cache, atomic output. CSV headers: invoice_id,customer,amount,paid. USD single-currency only.

## Limitations

Runs offline; scheduling and delivery are outside its scope. Browser preview is a JavaScript illustration; Python source is authoritative. Cache is file-based, not an invoice database across different CSV exports.

## Tests

Ten tests cover decimal parsing, invalid currency values, duplicate and overpaid rows, repeat-run caching, empty files, CSV headers and quoted customer names. Run the test command above to verify your environment.

## Design notes

Currency is parsed with Decimal and stored as integer cents. Each input file is identified by its SHA256 hash. Completed reports are cached in SQLite and written through a temporary file followed by atomic replacement.

MIT licensed. See LICENSE.