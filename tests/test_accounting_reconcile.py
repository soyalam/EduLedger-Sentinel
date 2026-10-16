
import pandas as pd

from src.accounting_reconcile import reconcile


def make_data():
    gateway = pd.DataFrame({
        "gateway_reference": ["GW-1", "GW-2"],
        "amount": [1000, 2000],
    })

    bank = pd.DataFrame({
        "bank_reference": ["GW-1", "GW-2"],
        "amount": [1000, 1950],
    })

    accounting = pd.DataFrame({
        "reference": ["GW-1", "GW-2"],
        "amount": [1000, 2000],
    })

    return gateway, bank, accounting


def test_three_way_match():
    gateway, bank, accounting = make_data()

    report = reconcile(gateway, bank, accounting)

    row = report[report["transaction_reference"] == "GW-1"].iloc[0]
    assert row["status"] == "MATCHED"


def test_bank_amount_mismatch():
    gateway, bank, accounting = make_data()

    report = reconcile(gateway, bank, accounting)

    row = report[report["transaction_reference"] == "GW-2"].iloc[0]
    assert row["status"] == "EXCEPTION"
    assert row["gateway_bank_difference"] == 50


def test_missing_accounting_entry():
    gateway, bank, accounting = make_data()
    accounting = accounting[accounting["reference"] != "GW-2"]

    report = reconcile(gateway, bank, accounting)

    row = report[report["transaction_reference"] == "GW-2"].iloc[0]
    assert row["status"] == "EXCEPTION"
    assert "MISSING_ACCOUNTING_ENTRY" in row["exceptions"]
