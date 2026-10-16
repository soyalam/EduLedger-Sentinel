# Test Plan — Phase 1

| ID | Scenario | Expected result |
|---|---|---|
| T01 | Gateway and bank reference and amount match | MATCHED |
| T02 | Reference exists but amount differs | AMOUNT_MISMATCH |
| T03 | Gateway reference absent from bank file | MISSING_BANK_ENTRY |
| T04 | Duplicate gateway reference | DUPLICATE_GATEWAY_REFERENCE |
| T05 | Bank row has no matching gateway reference | UNMATCHED_BANK_ENTRY |
| T06 | Duplicate bank reference | DUPLICATE_BANK_REFERENCE |
| T07 | Amounts differ by rounding beyond 0.01 | AMOUNT_MISMATCH |
| T08 | Reference differs only by whitespace/case | Normalize and compare |
