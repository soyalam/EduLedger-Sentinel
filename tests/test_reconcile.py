import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from reconcile import reconcile, normalize_reference

def test_normalize_reference():
    assert normalize_reference(" gw-1001 ") == "GW-1001"

def make_frames(gateway_rows, bank_rows):
    gateway = pd.DataFrame(gateway_rows, columns=[
        "gateway_reference", "transaction_date", "customer_id", "amount", "status"
    ])
    bank = pd.DataFrame(bank_rows, columns=[
        "bank_reference", "value_date", "amount", "entry_type"
    ])
    return gateway, bank

def test_matched():
    gw, bk = make_frames([["GW1","2026-10-01","C1",100.00,"SUCCESS"]],
                         [["GW1","2026-10-02",100.00,"SETTLEMENT"]])
    report, _ = reconcile(gw, bk)
    assert report.iloc[0]["reason"] == "REFERENCE_AND_AMOUNT_MATCH"

def test_amount_mismatch():
    gw, bk = make_frames([["GW1","2026-10-01","C1",100.00,"SUCCESS"]],
                         [["GW1","2026-10-02",99.00,"SETTLEMENT"]])
    report, _ = reconcile(gw, bk)
    assert report.iloc[0]["reason"] == "AMOUNT_MISMATCH"

def test_missing_bank_entry():
    gw, bk = make_frames([["GW1","2026-10-01","C1",100.00,"SUCCESS"]], [])
    report, _ = reconcile(gw, bk)
    assert report.iloc[0]["reason"] == "MISSING_BANK_ENTRY"

def test_duplicate_gateway_reference():
    gw, bk = make_frames([["GW1","2026-10-01","C1",100.00,"SUCCESS"],
                          ["GW1","2026-10-01","C1",100.00,"SUCCESS"]], [])
    report, _ = reconcile(gw, bk)
    assert all(report["reason"] == "DUPLICATE_GATEWAY_REFERENCE")
