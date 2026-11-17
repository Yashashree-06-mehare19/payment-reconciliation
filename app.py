import io
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Payment Reconciliation", page_icon="🔎", layout="wide")
BASE = Path(__file__).parent

from reconciliation import reconcile

@st.cache_data
def load_sample():
    tx = pd.read_csv(BASE / "data" / "transactions.csv", dtype={"transaction_id": str})
    bank = pd.read_csv(BASE / "data" / "settlements.csv", dtype={"transaction_id": str})
    return tx, bank

st.title("🔎 Payment Reconciliation")
st.caption("Compare platform transactions with bank settlements and explain month-end differences.")
with st.sidebar:
    st.header("Reconciliation settings")
    month = st.selectbox("Month to reconcile", ["2026-10", "2026-09", "2026-08"], index=0)
    row_tol = st.number_input("Per-record rounding tolerance (₹)", min_value=0.0, value=0.01, step=0.01, format="%.2f")
    agg_tol = st.number_input("Aggregate drift threshold (₹)", min_value=0.0, value=0.05, step=0.01, format="%.2f")
    st.divider()
    st.write("Upload your own CSVs or use the included synthetic sample data.")
    tx_file = st.file_uploader("Platform transactions CSV", type="csv")
    bank_file = st.file_uploader("Bank settlements CSV", type="csv")
try:
    if tx_file and bank_file:
        tx = pd.read_csv(tx_file, dtype={"transaction_id": str})
        bank = pd.read_csv(bank_file, dtype={"transaction_id": str})
    else:
        tx, bank = load_sample()
        st.info("Showing generated sample data. Upload both CSV files in the sidebar to analyze your own data.")
    report, duplicates, metrics = reconcile(tx, bank, month, row_tol, agg_tol)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Platform records", f"{len(tx):,}")
    c2.metric("Bank records", f"{len(bank):,}")
    c3.metric("Exceptions", f"{(report.status != 'Matched').sum() + len(duplicates):,}")
    c4.metric("Aggregate drift", f"₹{metrics['aggregate_rounding_drift']:.2f}", delta="Review" if metrics["rounding_flag"] else "Within threshold", delta_color="inverse" if metrics["rounding_flag"] else "normal")
    st.subheader("Discrepancy summary")
    categories = report[report["status"] != "Matched"]["status"].value_counts().rename_axis("Issue").reset_index(name="Count")
    if metrics["duplicate_rows"]:
        categories.loc[len(categories)] = ["Duplicate bank entry", metrics["duplicate_rows"]]
    if metrics["rounding_flag"]:
        categories.loc[len(categories)] = ["Aggregate rounding drift", 1]
    left,right = st.columns([1,1])
    with left:
        if len(categories): st.dataframe(categories, use_container_width=True, hide_index=True)
        else: st.success("No discrepancies found for this month.")
    with right:
        if len(categories): st.plotly_chart(px.bar(categories, x="Issue", y="Count", title="Exceptions by type"), use_container_width=True)
    if metrics["rounding_flag"]:
        st.warning(f"Aggregate rounding drift is ₹{metrics['aggregate_rounding_drift']:.2f}. Individual differences may be within ₹{row_tol:.2f}, but their sum exceeds the ₹{agg_tol:.2f} threshold.")
    if len(duplicates):
        st.subheader("Duplicate bank entries")
        st.dataframe(duplicates, use_container_width=True, hide_index=True)
    st.subheader("Reconciliation details")
    status_filter = st.multiselect("Filter by status", sorted(report.status.unique()), default=sorted(report.status.unique()))
    view = report[report.status.isin(status_filter)]
    st.dataframe(view, use_container_width=True, hide_index=True)
    csv = report.to_csv(index=False).encode("utf-8")
    st.download_button("Download reconciliation report (CSV)", csv, "reconciliation_report.csv", "text/csv")
    st.caption("Assumptions: transaction_id is the stable matching key; amounts are in INR; settlement dates determine the bank month; the first bank row is used for matching and additional rows are reported as duplicates; refunds are identified by type='refund'.")
except Exception as e:
    st.error(f"Could not reconcile these files: {e}")
    st.markdown("Expected columns — transactions: `transaction_id, transaction_date, type, amount`; settlements: `transaction_id, settlement_date, amount`.")
