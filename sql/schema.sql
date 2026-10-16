-- Proposed relational schema for the EduLedger Sentinel learning project.
-- Synthetic data only. Dialect may need minor adjustment for your database.
CREATE TABLE gateway_transactions (
    gateway_reference VARCHAR(40) NOT NULL,
    transaction_date DATE NOT NULL,
    customer_id VARCHAR(40) NOT NULL,
    amount DECIMAL(12,2) NOT NULL CHECK (amount >= 0),
    status VARCHAR(20) NOT NULL
);

CREATE TABLE bank_statement_lines (
    bank_reference VARCHAR(40),
    value_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    entry_type VARCHAR(30) NOT NULL
);

CREATE TABLE reconciliation_results (
    result_id INTEGER PRIMARY KEY,
    gateway_reference VARCHAR(40),
    bank_reference VARCHAR(40),
    gateway_amount DECIMAL(12,2),
    bank_amount DECIMAL(12,2),
    status VARCHAR(20) NOT NULL,
    reason VARCHAR(60) NOT NULL,
    reviewed_by VARCHAR(80),
    resolution_note VARCHAR(500),
    created_at TIMESTAMP NOT NULL
);
