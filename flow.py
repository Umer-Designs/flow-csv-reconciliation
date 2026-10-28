"""Reconcile invoice CSVs and atomically write cached JSON reports."""

import argparse
import csv
import json
import os
import sqlite3
import tempfile
from pathlib import Path
from reconciliation import MAX_BYTES, money, reconcile_csv


def process(source, output, state):
    with open(source, "rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    report = reconcile_csv(raw)
    with sqlite3.connect(state) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS runs(hash TEXT PRIMARY KEY, report TEXT NOT NULL)"
        )
        prior = connection.execute(
            "SELECT report FROM runs WHERE hash=?", (report["sha256"],)
        ).fetchone()
        if prior:
            report = json.loads(prior[0])
            report["cached"] = True
        else:
            connection.execute(
                "INSERT OR IGNORE INTO runs VALUES(?,?)",
                (report["sha256"], json.dumps(report)),
            )
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(dir=target.parent, suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2)
        os.replace(name, target)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("--output", default="report.json")
    parser.add_argument("--state", default="runs.db")
    args = parser.parse_args()
    try:
        print(json.dumps(process(args.source, args.output, args.state)["totals"]))
    except (OSError, ValueError, UnicodeError, csv.Error) as error:
        parser.exit(1, f"Processing failed: {error}\n")
