
import pandas as pd

from src.exception_report import main


def test_exception_report_generation(tmp_path, monkeypatch):
    import src.exception_report as module

    sample = pd.DataFrame([
        {
            "transaction_reference": "GW-1",
            "status": "MATCHED",
            "exceptions": "",
        },
        {
            "transaction_reference": "GW-2",
            "status": "EXCEPTION",
            "exceptions": "GATEWAY_BANK_AMOUNT_MISMATCH",
        },
        {
            "transaction_reference": "GW-3",
            "status": "EXCEPTION",
            "exceptions": "MISSING_ACCOUNTING_ENTRY",
        },
    ])

    input_file = tmp_path / "accounting_reconciliation.csv"
    sample.to_csv(input_file, index=False)

    monkeypatch.setattr(module, "INPUT_FILE", input_file)
    monkeypatch.setattr(module, "OUTPUT_DIR", tmp_path)

    main()

    result = pd.read_csv(tmp_path / "exception_report.csv")

    assert len(result) == 2
    assert set(result["transaction_reference"]) == {"GW-2", "GW-3"}
    assert result.loc[
        result["transaction_reference"] == "GW-2", "priority"
    ].iloc[0] == "HIGH"
    assert result.loc[
        result["transaction_reference"] == "GW-3", "priority"
    ].iloc[0] == "MEDIUM"
