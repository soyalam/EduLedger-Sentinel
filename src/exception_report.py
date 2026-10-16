
"""Generate an audit-friendly report of reconciliation exceptions."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "output" / "accounting_reconciliation.csv"
OUTPUT_DIR = ROOT / "output"


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Reconciliation report not found: {INPUT_FILE}. "
            "Run accounting_reconcile.py first."
        )

    report = pd.read_csv(INPUT_FILE)

    required = {
        "transaction_reference",
        "status",
        "exceptions",
    }
    missing = required - set(report.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    exceptions = report.loc[
        report["status"].eq("EXCEPTION")
    ].copy()

    exceptions["priority"] = exceptions["exceptions"].apply(
        lambda value: (
            "HIGH"
            if pd.notna(value) and any(
                issue in str(value)
                for issue in [
                    "DUPLICATE",
                    "AMOUNT_MISMATCH",
                ]
            )
            else "MEDIUM"
        )
    )

    exceptions.to_csv(
        OUTPUT_DIR / "exception_report.csv",
        index=False,
    )

    print(f"Total transactions: {len(report)}")
    print(f"Exceptions requiring review: {len(exceptions)}")
    print(
        f"High-priority exceptions: "
        f"{(exceptions['priority'] == 'HIGH').sum()}"
    )
    print(
        f"Medium-priority exceptions: "
        f"{(exceptions['priority'] == 'MEDIUM').sum()}"
    )
    print(f"Saved report: {OUTPUT_DIR / 'exception_report.csv'}")


if __name__ == "__main__":
    main()
