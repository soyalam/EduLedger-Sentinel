
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"

st.set_page_config(
    page_title="EduLedger Sentinel",
    page_icon="📊",
    layout="wide",
)

st.title("EduLedger Sentinel")
st.caption("Financial Reconciliation & Exception Monitoring")

@st.cache_data
def load_csv(path):
    return pd.read_csv(path)

try:
    gateway = load_csv(DATA / "gateway_transactions.csv")
    bank = load_csv(DATA / "bank_statement.csv")
    accounting = load_csv(DATA / "accounting_extract.csv")
except FileNotFoundError as exc:
    st.error(f"Required input file not found: {exc}")
    st.stop()

if st.button("Run reconciliation", type="primary"):
    try:
        from accounting_reconcile import reconcile

        report = reconcile(gateway, bank, accounting)

        OUTPUT.mkdir(exist_ok=True)
        report.to_csv(OUTPUT / "accounting_reconciliation.csv", index=False)
        st.session_state["report"] = report
    except Exception as exc:
        st.error(f"Reconciliation failed: {exc}")

report = st.session_state.get("report")

if report is None:
    st.info("Click **Run reconciliation** to generate the latest results.")
    st.stop()

total = len(report)
matched = int((report["status"] == "MATCHED").sum())
exceptions = int((report["status"] == "EXCEPTION").sum())
match_rate = matched / total * 100 if total else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total references", total)
col2.metric("Matched", matched)
col3.metric("Exceptions", exceptions)
col4.metric("Match rate", f"{match_rate:.1f}%")

st.subheader("Reconciliation status")
st.bar_chart(
    pd.DataFrame({
        "Count": [matched, exceptions]
    }, index=["Matched", "Exceptions"])
)

st.subheader("Transaction reconciliation")
search = st.text_input("Search transaction reference")
status_filter = st.selectbox(
    "Filter status",
    ["All", "MATCHED", "EXCEPTION"],
)

filtered = report.copy()

if search:
    filtered = filtered[
        filtered["transaction_reference"]
        .astype(str)
        .str.contains(search, case=False, na=False)
    ]

if status_filter != "All":
    filtered = filtered[filtered["status"] == status_filter]

st.dataframe(filtered, use_container_width=True, hide_index=True)

st.subheader("Download reports")
st.download_button(
    "Download full reconciliation CSV",
    data=report.to_csv(index=False).encode("utf-8"),
    file_name="accounting_reconciliation.csv",
    mime="text/csv",
)

exception_report = report[report["status"] == "EXCEPTION"]

st.download_button(
    "Download exceptions CSV",
    data=exception_report.to_csv(index=False).encode("utf-8"),
    file_name="exception_report.csv",
    mime="text/csv",
)
