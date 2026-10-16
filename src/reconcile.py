
"""Phase 1 prototype for reconciling synthetic gateway and bank data."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"


def normalize_reference(value):
    """Standardize transaction references before matching."""
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def reconcile(gateway: pd.DataFrame, bank: pd.DataFrame):
    """Compare gateway transactions against bank statement entries."""
    gateway = gateway.copy()
    bank = bank.copy()

    gateway["normalized_ref"] = gateway["gateway_reference"].map(
        normalize_reference
    )
    bank["normalized_ref"] = bank["bank_reference"].map(
        normalize_reference
    )

    gateway_counts = gateway["normalized_ref"].value_counts()
    bank_counts = bank["normalized_ref"].value_counts()

    bank_groups = {
        ref: group
        for ref, group in bank.groupby("normalized_ref", dropna=False)
    }

    rows = []

    for _, gw in gateway.iterrows():
        ref = gw["normalized_ref"]
        matches = bank_groups.get(ref, bank.iloc[0:0])

        status = "EXCEPTION"
        reason = ""
        bank_reference = None
        bank_amount = None
        bank_date = None
        amount_difference = None

        if ref and gateway_counts.get(ref, 0) > 1:
            reason = "DUPLICATE_GATEWAY_REFERENCE"

        elif ref and bank_counts.get(ref, 0) > 1:
            reason = "DUPLICATE_BANK_REFERENCE"

        elif len(matches) == 0:
            reason = "MISSING_BANK_ENTRY"

        else:
            bank_row = matches.iloc[0]
            bank_reference = bank_row["bank_reference"]
            bank_amount = round(float(bank_row["amount"]), 2)
            bank_date = bank_row["value_date"]

            gateway_amount = round(float(gw["amount"]), 2)
            amount_difference = round(
                gateway_amount - bank_amount, 2
            )

            if amount_difference == 0:
                status = "MATCHED"
                reason = "REFERENCE_AND_AMOUNT_MATCH"
            else:
                reason = "AMOUNT_MISMATCH"

        rows.append({
            "gateway_reference": gw["gateway_reference"],
            "transaction_date": gw["transaction_date"],
            "customer_id": gw["customer_id"],
            "gateway_amount": round(float(gw["amount"]), 2),
            "bank_reference": bank_reference,
            "bank_amount": bank_amount,
            "amount_difference": amount_difference,
            "bank_value_date": bank_date,
            "status": status,
            "reason": reason,
        })

    report = pd.DataFrame(rows)

    # Find bank entries that have no gateway reference.
    matched_refs = set(gateway["normalized_ref"])
    unmatched_bank = bank[
        ~bank["normalized_ref"].isin(matched_refs)
    ]

    unmatched_rows = []

    for _, row in unmatched_bank.iterrows():
        unmatched_rows.append({
            "gateway_reference": None,
            "transaction_date": None,
            "customer_id": None,
            "gateway_amount": None,
            "bank_reference": row["bank_reference"],
            "bank_amount": round(float(row["amount"]), 2),
            "amount_difference": None,
            "bank_value_date": row["value_date"],
            "status": "EXCEPTION",
            "reason": "UNMATCHED_BANK_ENTRY",
        })

    if unmatched_rows:
        report = pd.concat(
            [report, pd.DataFrame(unmatched_rows)],
            ignore_index=True,
        )

    exceptions = report[report["status"] == "EXCEPTION"].copy()
    return report, exceptions


def main():
    OUTPUT.mkdir(exist_ok=True)

    gateway = pd.read_csv(DATA / "gateway_transactions.csv")
    bank = pd.read_csv(DATA / "bank_statement.csv")

    report, exceptions = reconcile(gateway, bank)

    report.to_csv(OUTPUT / "reconciliation_report.csv", index=False)
    exceptions.to_csv(OUTPUT / "exception_register.csv", index=False)

    print(f"Report rows: {len(report)}")
    print(f"Matched rows: {(report['status'] == 'MATCHED').sum()}")
    print(f"Exception rows: {(report['status'] == 'EXCEPTION').sum()}")
    print(f"Saved reports in: {OUTPUT}")


if __name__ == "__main__":
    main()
