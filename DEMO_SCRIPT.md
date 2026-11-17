# 90-second demo video script

1. **0:00–0:10 — Introduce the problem.** “This dashboard reconciles payment-platform transactions against bank settlements to explain month-end differences.”
2. **0:10–0:20 — Show inputs.** Point out the two included CSV datasets and the option to upload a company's own files.
3. **0:20–0:40 — Show planted exceptions.** Select October 2026. Show the next-month settlement, duplicate bank entry, and unmatched refund in the discrepancy summary and details.
4. **0:40–0:55 — Explain rounding.** Point out that each small per-record difference is within the row tolerance, but their cumulative difference is ₹0.20 and exceeds the aggregate threshold.
5. **0:55–1:10 — Show report.** Filter the detail table and click “Download reconciliation report (CSV)”.
6. **1:10–1:25 — Close with limitations.** “This is a prototype. Before production, we would add robust settlement references, decimal-safe money calculations, fees, partial settlements, chargebacks, currencies, and audit controls.”
