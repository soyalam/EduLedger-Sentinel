
"""Three-way reconciliation for synthetic finance data."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"


def normalize_reference(value):
    """Standardize references before comparing records."""
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def reconcile_three_sources(gateway, bank, accounting):
    """Compare payment gateway, bank, and accounting records."""
    gateway = gateway.copy()
    bank = bank.copy()
    accounting = accounting.copy()

    gateway["normalized_ref"] = gateway["gateway_reference"].map(
        normalize_reference
    )
    bank["normalized_ref"] = bank["bank_reference"].map(
        normalize_reference
    )
    accounting["normalized_ref"] = accounting["reference"].map(
        normalize_reference
    )

    references = sorted(
        ref
        for ref in (
            set(gateway["normalized_ref"])
            | set(bank["normalized_ref"])
            | set(accounting["normalized_ref"])
        )
        if ref
    )

    rows = []

    for ref in references:
        g = gateway[gateway["normalized_ref"] == ref]
        b = bank[bank["normalized_ref"] == ref]
        a = accounting[accounting["normalized_ref"] == ref]

        reasons = []

        # Detect duplicate references in any source.
        if len(g) > 1:
            reasons.append("DUPLICATE_GATEWAY_REFERENCE")
        if len(b) > 1:
            reasons.append("DUPLICATE_BANK_REFERENCE")
        if len(a) > 1:
            reasons.append("DUPLICATE_ACCOUNTING_REFERENCE")

        # Detect missing records.
        if len(g) == 0:
            reasons.append("GATEWAY_ENTRY_MISSING")
        if len(b) == 0:
            reasons.append("BANK_ENTRY_MISSING")
        if len(a) == 0:
            reasons.append("ACCOUNTING_ENTRY_MISSING")

        # Use amounts only when a source has exactly one record.
        gateway_amount = (
            round(float(g.iloc[0]["amount"]), 2)
            if len(g) == 1 else None
        )
        bank_amount = (
            round(float(b.iloc[0]["amount"]), 2)
            if len(b) == 1 else None
        )
        accounting_amount = (
            round(float(a.iloc[0]["amount"]), 2)
            if len(a) == 1 else None
        )

        # Compare amounts between available, unambiguous records.
        def check_difference(left, right, reason):
            if left is not None and right is not None and left != right:
                reasons.append(reason)

        check_difference(
            gateway_amount, bank_amount,
            "GATEWAY_BANK_AMOUNT_MISMATCH"
        )
        check_difference(
            gateway_amount, accounting_amount,
            "GATEWAY_ACCOUNTING_AMOUNT_MISMATCH"
        )
        check_difference(
            bank_amount, accounting_amount,
            "BANK_ACCOUNTING_AMOUNT_MISMATCH"
        )

        rows.append({
            "reference": ref,
            "gateway_record_count": len(g),
            "gateway_amount": gateway_amount,
            "bank_record_count": len(b),
            "bank_amount": bank_amount,
            "accounting_record_count": len(a),
            "accounting_document": (
                a.iloc[0]["accounting_document"]
                if len(a) == 1 else None
            ),
            "accounting_amount": accounting_amount,
            "bank_minus_gateway": (
                round(bank_amount - gateway_amount, 2)
                if bank_amount is not None
                and gateway_amount is not None else None
            ),
            "accounting_minus_gateway": (
                round(accounting_amount - gateway_amount, 2)
                if accounting_amount is not None
                and gateway_amount is not None else None
            ),
            "accounting_minus_bank": (
                round(accounting_amount - bank_amount, 2)
                if accounting_amount is not None
                and bank_amount is not None else None
            ),
            "status": "MATCHED" if not reasons else "EXCEPTION",
            "reason": (
                "ALL_THREE_SOURCES_MATCH"
                if not reasons else "; ".join(reasons)
            ),
        })

    report = pd.DataFrame(rows)
    exceptions = report[report["status"] == "EXCEPTION"].copy()

    return report, exceptions


def main():
    OUTPUT.mkdir(exist_ok=True)

    gateway = pd.read_csv(DATA / "gateway_transactions.csv")
    bank = pd.read_csv(DATA / "bank_statement.csv")
    accounting = pd.read_csv(DATA / "accounting_extract.csv")

    report, exceptions = reconcile_three_sources(
        gateway, bank, accounting
    )

    report.to_csv(
        OUTPUT / "three_way_reconciliation_report.csv",
        index=False
    )
    exceptions.to_csv(
        OUTPUT / "three_way_exception_register.csv",
        index=False
    )

    print(f"Reference rows: {len(report)}")
    print(
        "Matched references: "
        f"{(report['status'] == 'MATCHED').sum()}"
    )
    print(
        "Exception references: "
        f"{(report['status'] == 'EXCEPTION').sum()}"
    )
    print(f"Saved reports in: {OUTPUT}")


if __name__ == "__main__":
    main()
