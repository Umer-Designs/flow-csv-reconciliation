# Flow CSV Reconciliation

Independent portfolio project by Umer Khalid, 2026. All example data is fictional.

## Run

```text
python flow.py sample.csv --output report.json --state runs.db
# Optional test dependency
python -m pip install pytest
python -m pytest -q
```

Use Python 3.12+ or Node 22+ with pnpm, as applicable. Create and activate a virtual environment for Python dependencies.

## Features

Python standard library pipeline. Decimal validation, duplicate rejection, outstanding totals, deterministic summary, content-addressed SQLite cache, atomic output. CSV headers: invoice_id,customer,amount,paid. USD single-currency only.

## Limitations

No LLM or external API integration. No email delivery or scheduling. Browser preview is a JavaScript illustration; Python source is authoritative. Cache is file-based, not an invoice database across different CSV exports.

## Tests

Tests live alongside the source and cover business rules and error cases. See the portfolio delivery report for the actual validation results.

## Explain this project

Trace one input through validation, state change, and output. Explain the data representation and one failure path. Modify a validation rule and update its test before discussing the project in an interview.

MIT licensed. No employment, client work or production outcomes are claimed.
