# Payment Reconciliation Dashboard

A Streamlit application that compares payment-platform transaction records with bank settlement records and surfaces month-end exceptions.

## Run locally

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Test

```bash
pytest -q
```

## CSV schemas

Transactions: `transaction_id, transaction_date, type, amount`

Settlements: `transaction_id, settlement_date, amount`

Upload both files in the sidebar. If either file is not uploaded, the app loads the included synthetic sample.

## Deliberate test-data exceptions

- TX1021: October transaction settled on November 1.
- TX1001–TX1020: each bank amount is one paisa higher; the individual variance is within the default ₹0.01 tolerance, while the aggregate drift is ₹0.20.
- TX1002: appears twice in the bank dataset.
- TX1022: refund has no matching settlement under its transaction ID; TX9999 is an unmatched bank-side refund-like entry.

## Assumptions and limitations

- `transaction_id` is the stable join key. Real processors may require matching on multiple fields or reference IDs.
- Amounts are INR and are compared as numeric values. Production financial calculations should use integer paise or decimal arithmetic, not binary floating point.
- The first settlement row for a transaction ID is used for matching; additional rows are reported as duplicates.
- A refund is identified by `type=refund`. Real systems need explicit refund IDs and links to original payments.
- The sample app does not model fees, chargebacks, partial settlements, reversals, multiple currencies, bank holidays, or settlement cut-off times.
- The month selector is currently a small demo list; production should derive available months from uploaded data.
