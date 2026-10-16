
"""Phase 2: Three-way reconciliation of gateway, bank, and accounting data."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"


def normalize_reference(value):
    """Normalize transaction references for reliable matching."""
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def load_csv(filename):
    """Load a CSV and validate that it contains data."""
    path = DATA / filename
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")

    return pd.read_csv(path)


def reconcile(gateway, bank, accounting):
    """Compare gateway transactions, bank entries, and accounting records."""
    gateway = gateway.copy()
    bank = bank.copy()
    accounting = accounting.copy()

    required_columns = {
        "gateway": (gateway, {"gateway_reference", "amount"}),
        "bank": (bank, {"bank_reference", "amount"}),
        "accounting": (accounting, {"reference", "amount"}),
    }

    for name, (frame, required) in required_columns.items():
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(
                f"{name} CSV is missing columns: {sorted(missing)}"
            )

    for frame, column in [
        (gateway, "gateway_reference"),
        (bank, "bank_reference"),
        (accounting, "reference"),
    ]:
        frame["_ref"] = frame[column].map(normalize_reference)

    for name, frame in [
        ("gateway", gateway),
        ("bank", bank),
        ("accounting", accounting),
    ]:
        if frame["_ref"].eq("").any():
            raise ValueError(
                f"{name} data contains blank transaction references"
            )
        frame["amount"] = pd.to_numeric(frame["amount"], errors="raise")

    # Preserve all references, including entries found in only one source.
    references = sorted(
        set(gateway["_ref"]) | set(bank["_ref"]) | set(accounting["_ref"])
    )

    rows = []

    for ref in references:
        g = gateway[gateway["_ref"] == ref]
        b = bank[bank["_ref"] == ref]
        a = accounting[accounting["_ref"] == ref]

        issues = []

        if len(g) > 1:
            issues.append("DUPLICATE_GATEWAY_REFERENCE")
        if len(b) > 1:
            issues.append("DUPLICATE_BANK_REFERENCE")
        if len(a) > 1:
            issues.append("DUPLICATE_ACCOUNTING_REFERENCE")

        gateway_amount = g["amount"].sum() if len(g) else None
        bank_amount = b["amount"].sum() if len(b) else None
        accounting_amount = a["amount"].sum() if len(a) else None

        if len(g) == 0:
            issues.append("MISSING_GATEWAY_ENTRY")
        if len(b) == 0:
            issues.append("MISSING_BANK_ENTRY")
        if len(a) == 0:
            issues.append("MISSING_ACCOUNTING_ENTRY")

        if len(g) and len(b) and gateway_amount != bank_amount:
            issues.append("GATEWAY_BANK_AMOUNT_MISMATCH")

        if len(g) and len(a) and gateway_amount != accounting_amount:
            issues.append("GATEWAY_ACCOUNTING_AMOUNT_MISMATCH")

        if len(b) and len(a) and bank_amount != accounting_amount:
            issues.append("BANK_ACCOUNTING_AMOUNT_MISMATCH")

        rows.append({
            "transaction_reference": ref,
            "gateway_amount": gateway_amount,
            "bank_amount": bank_amount,
            "accounting_amount": accounting_amount,
            "gateway_bank_difference": (
                gateway_amount - bank_amount
                if gateway_amount is not None and bank_amount is not None
                else None
            ),
            "gateway_accounting_difference": (
                gateway_amount - accounting_amount
                if gateway_amount is not None and accounting_amount is not None
                else None
            ),
            "bank_accounting_difference": (
                bank_amount - accounting_amount
                if bank_amount is not None and accounting_amount is not None
                else None
            ),
            "gateway_rows": len(g),
            "bank_rows": len(b),
            "accounting_rows": len(a),
            "status": "MATCHED" if not issues else "EXCEPTION",
            "exceptions": ";".join(issues) if issues else "",
        })

    return pd.DataFrame(rows)


def main():
    gateway = load_csv("gateway_transactions.csv")
    bank = load_csv("bank_statement.csv")
    accounting = load_csv("accounting_extract.csv")

    report = reconcile(gateway, bank, accounting)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT / "accounting_reconciliation.csv"
    report.to_csv(report_path, index=False)

    print(f"Report rows: {len(report)}")
    print(f"Matched rows: {(report['status'] == 'MATCHED').sum()}")
    print(f"Exception rows: {(report['status'] == 'EXCEPTION').sum()}")
    print(f"Saved report: {report_path}")


if __name__ == "__main__":
    main()
