
# EduLedger Sentinel

A Python-based financial reconciliation and exception-monitoring tool that compares payment gateway transactions, bank settlements, and accounting records.

## Project Overview

EduLedger Sentinel helps identify discrepancies between financial data sources and generates an exception report for investigation.

## Features

- Transaction reference normalization
- Three-way reconciliation of gateway, bank, and accounting data
- Detection of missing transaction records
- Duplicate reference detection
- Identification of amount mismatches
- Calculation of reconciliation differences
- Automated exception reporting with priority labels
- Automated tests using pytest

## Technology Stack

- Python 3.13
- Pandas
- CSV-based financial data
- Pytest

## Project Structure

```text
EduLedger_Sentinel/
├── data/
│   ├── gateway_transactions.csv
│   ├── bank_statement.csv
│   ├── accounting_extract.csv
│   └── accounting_ledger.csv
├── src/
│   ├── reconcile.py
│   ├── accounting_reconcile.py
│   └── exception_report.py
├── tests/
├── output/
├── README.md
└── requirements.txt
```

## Installation

Install the required dependencies:

```bash
py -3.13 -m pip install -r requirements.txt
```

## How to Run

### 1. Run basic reconciliation

```bash
py -3.13 src/reconcile.py
```

### 2. Run three-way reconciliation

```bash
py -3.13 src/accounting_reconcile.py
```

### 3. Generate the exception report

```bash
py -3.13 src/exception_report.py
```

### 4. Run automated tests

```bash
py -3.13 -m pytest tests -v
```

## Output Files

- `output/accounting_reconciliation.csv` — transaction-level reconciliation results
- `output/exception_report.csv` — exceptions requiring investigation

## Exception Types

Examples include:

- Missing bank entries
- Missing accounting entries
- Missing gateway entries
- Duplicate transaction references
- Gateway-to-bank amount mismatches
- Gateway-to-accounting amount mismatches
- Bank-to-accounting amount mismatches

## Testing

The project includes automated tests for reference normalization, successful matches, amount discrepancies, duplicate references, missing entries, and exception report generation.

## Disclaimer

This project uses sample data for educational and portfolio purposes. It is not a production accounting system, and exception priorities are illustrative rather than formal financial-risk classifications.

## Future Improvements

- Excel report generation
- Dashboard for reconciliation metrics
- Configurable tolerance thresholds
- Structured logging and error handling
- Additional accounting-ledger validation
