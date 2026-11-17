# Assessment submission guide

## 1. Brainstorming thread
Use the actual ChatGPT conversation in which the problem was decomposed, assumptions were chosen, and the application was planned. Export/share the conversation as required by the assessor; do not edit it or present a reconstructed conversation as a verbatim transcript.

## 2. Distilled prompt and raw prompt

### Distilled prompt
Build a Python + Streamlit payment reconciliation dashboard. It must accept platform transaction and bank settlement CSVs, match records by transaction ID, identify next-month settlements, aggregate rounding drift, duplicate bank entries, and refunds without matching originals. Include synthetic sample data with each gap deliberately planted, explain assumptions, provide downloadable results, and include automated tests.

### Raw prompt (paste this as one prompt into Claude Code or Cursor)
You are a senior Python engineer. In this repository, build and verify a small but polished payment reconciliation application for a payments company.

Business problem: the platform records each payment immediately, while the bank settles funds 1–2 days later. At month-end, platform transaction totals and bank settlement totals should reconcile. The application must show exactly why they do not.

Requirements:
1. Use Python, Pandas, and Streamlit. Build a dashboard that can load the included sample CSVs and allow the user to upload their own two CSV files.
2. Platform CSV schema: transaction_id, transaction_date, type, amount. Bank CSV schema: transaction_id, settlement_date, amount. Validate required columns, dates, and numeric amounts and show understandable errors.
3. Match records using transaction_id. Report missing/unmatched records, amount mismatches, duplicates in the bank dataset, refunds without a matching original/settlement, and transactions in the selected month that settle in the following month.
4. Deliberately plant all required cases in synthetic test data: a transaction settling in the following month; a small per-record rounding difference whose cumulative sum crosses a threshold; a duplicate entry in one dataset; and a refund with no matching original transaction.
5. Make the rounding case meaningful: individual differences should be within a configurable per-row tolerance, but their aggregate should exceed a configurable aggregate threshold.
6. Show summary metrics, exception categories, a detailed reconciliation table, and a CSV download.
7. State assumptions visibly in the app and README. Do not claim this is production-ready. Explain risks such as partial settlements, fees, chargebacks, multiple currencies, ambiguous identifiers, and floating-point money arithmetic.
8. Add automated tests for every planted gap type, at least one correctly matched transaction, and invalid input schema.
9. Keep the code readable and modular. Run the tests and fix failures. Do not fabricate test results. At the end, summarize changed files, test command/results, how to run locally, and any limitations.

Work in the existing repository rather than creating a second nested project. Preserve the sample data and make sure `pytest -q` passes.

## 3. Claude Code / Cursor execution thread
Paste the raw prompt above into Claude Code or Cursor with this project folder open. Keep the actual full execution transcript, including errors and corrections. Do not claim this guide is a Claude Code transcript; the transcript must come from your real run.

## 4. Test cases
See `tests/test_reconciliation.py`. Run `pytest -q`; capture the real terminal output for submission.

## 5. Working output
Run locally using the README. Deploy by following `DEPLOYMENT.md`, then add the actual public URL. Record the demo using `DEMO_SCRIPT.md`. Use the exact three-sentence limitations statement in `PRODUCTION_LIMITATIONS.md` if desired.
