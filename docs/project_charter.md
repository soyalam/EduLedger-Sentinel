# Project Charter — EduLedger Sentinel

## 1. Objective
Create a demonstrable learning prototype that helps a fictional education provider reconcile payment-gateway transactions against bank settlement lines and track exceptions for review.

## 2. Business scenario
A fictional training provider collects learner fees through an online payment gateway. Finance receives a gateway transaction file and a bank statement file. Differences can occur because of delayed settlement, duplicate references, incorrect amounts, refunds, or missing entries.

## 3. Goals
- Apply deterministic matching rules that are easy to explain.
- Detect common discrepancies without silently changing source data.
- Produce an auditable report showing the match status and reason.
- Prepare for later integration with SAP S/4HANA FI concepts.

## 4. Out of scope for Phase 1
- No connection to a real SAP system.
- No real student, bank, or company data.
- No automated posting or payment execution.
- No claim of production readiness or completed SAP implementation.

## 5. Proposed matching rules
1. Normalize transaction references by trimming whitespace and uppercasing.
2. If a gateway reference occurs more than once, flag all rows for that reference as `DUPLICATE_GATEWAY_REFERENCE`.
3. If exactly one bank row has the reference and amounts match to two decimal places, mark `MATCHED`.
4. If exactly one bank row has the reference but amounts differ, mark `AMOUNT_MISMATCH`.
5. If no bank row has the reference, mark `MISSING_BANK_ENTRY`.
6. If multiple bank rows have the same reference, flag `DUPLICATE_BANK_REFERENCE`.
7. Bank rows with no gateway reference match are reported as `UNMATCHED_BANK_ENTRY`.

## 6. Success criteria
- All supplied synthetic test scenarios are correctly classified.
- Reports preserve source references and amounts.
- Tests pass and limitations are documented.
- The learner can explain each rule and demonstrate the script.

## 7. Evidence and honesty
Only label a task as performed in SAP after it has actually been executed in the Entri-provided practice system. Screenshots, transaction IDs, and configuration evidence must be genuine and must not contain confidential information.
