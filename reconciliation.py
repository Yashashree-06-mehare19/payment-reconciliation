import pandas as pd

REQUIRED_TX = {"transaction_id", "transaction_date", "type", "amount"}
REQUIRED_ST = {"transaction_id", "settlement_date", "amount"}

def validate(df, required, label):
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{label} file is missing columns: {', '.join(sorted(missing))}")

def reconcile(tx, stl, month, row_tolerance=0.01, aggregate_tolerance=0.05):
    tx = tx.copy(); stl = stl.copy()
    validate(tx, REQUIRED_TX, "Transactions")
    validate(stl, REQUIRED_ST, "Settlements")
    tx["transaction_id"] = tx["transaction_id"].astype(str)
    stl["transaction_id"] = stl["transaction_id"].astype(str)
    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"], errors="coerce")
    stl["settlement_date"] = pd.to_datetime(stl["settlement_date"], errors="coerce")
    tx["amount"] = pd.to_numeric(tx["amount"], errors="coerce")
    stl["amount"] = pd.to_numeric(stl["amount"], errors="coerce")
    if tx[["transaction_date", "amount"]].isna().any().any() or stl[["settlement_date", "amount"]].isna().any().any():
        raise ValueError("Dates and amounts must contain valid values.")
    # Keep the first settlement for matching; separately report repeated rows.
    duplicate_mask = stl.duplicated("transaction_id", keep="first")
    duplicates = stl.loc[duplicate_mask].copy()
    stl_unique = stl.drop_duplicates("transaction_id", keep="first")
    merged = tx.merge(stl_unique, on="transaction_id", how="outer", suffixes=("_tx", "_bank"), indicator=True)
    month_period = pd.Period(month, freq="M")
    tx_month = merged["transaction_date"].dt.to_period("M") == month_period
    bank_month = merged["settlement_date"].dt.to_period("M") == month_period
    results = []
    for _, r in merged.iterrows():
        tid = r["transaction_id"]
        in_tx = r["_merge"] != "right_only"
        in_bank = r["_merge"] != "left_only"
        typ = str(r.get("type", "payment")).lower() if in_tx else "unknown"
        tx_date = r.get("transaction_date")
        bank_date = r.get("settlement_date")
        tx_amt = r.get("amount_tx")
        bank_amt = r.get("amount_bank")
        status = "Matched"
        detail = "Transaction and settlement agree."
        if in_tx and typ == "refund" and not in_bank:
            status, detail = "Unmatched refund", "Refund has no corresponding bank settlement."
        elif not in_tx:
            status, detail = "Unmatched bank entry", "Bank settlement has no platform transaction."
        elif not in_bank:
            if pd.notna(tx_date) and tx_date.to_period("M") == month_period:
                status, detail = "Missing settlement", "No settlement record found for this transaction."
            else:
                status, detail = "Outside selected month", "Transaction is not in the selected month."
        elif pd.notna(tx_date) and tx_date.to_period("M") == month_period and pd.notna(bank_date) and bank_date.to_period("M") != month_period:
            status, detail = "Next-month settlement", f"Settled on {bank_date:%Y-%m-%d}, outside the selected month."
        elif abs(float(tx_amt) - float(bank_amt)) > row_tolerance:
            status, detail = "Amount mismatch", f"Platform {tx_amt:.2f} vs bank {bank_amt:.2f}."
        elif abs(float(tx_amt) - float(bank_amt)) > 0:
            status, detail = "Within row rounding tolerance", "Small per-record difference; included in aggregate drift check."
        results.append({"transaction_id": tid, "type": typ, "transaction_date": tx_date, "settlement_date": bank_date,
                        "platform_amount": tx_amt, "bank_amount": bank_amt,
                        "difference": (float(bank_amt)-float(tx_amt)) if in_tx and in_bank else None,
                        "status": status, "details": detail})
    report = pd.DataFrame(results)
    # Aggregate rounding: sum small per-row differences for selected-month transactions
    matched = report[(report["transaction_date"].notna()) & (report["transaction_date"].dt.to_period("M") == month_period) &
                     (report["settlement_date"].notna()) & (report["settlement_date"].dt.to_period("M") == month_period) &
                     (report["type"].str.lower() == "payment")]
    drift = float(matched["difference"].fillna(0).sum())
    rounding_flag = abs(drift) > aggregate_tolerance
    dup_count = int(len(duplicates))
    refund_count = int((report["status"] == "Unmatched refund").sum())
    next_month_count = int((report["status"] == "Next-month settlement").sum())
    return report, duplicates, {"aggregate_rounding_drift": drift, "rounding_flag": rounding_flag,
                                "duplicate_rows": dup_count, "unmatched_refunds": refund_count,
                                "next_month_settlements": next_month_count}

