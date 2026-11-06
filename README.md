# Assignment 3 — Invoice Extraction Comparison

Completed on 6 November 2026. All four methods processed the same 50 source invoice PDFs. The final results and report are available below; no API run is required to review them.

## Final results

| Method | Invoices | Correct fields | Field accuracy |
|---|---:|---:|---:|
| 1 — Programmatic rules | 50 | 1,496 / 2,346 | 63.8% |
| 2 — Gemini 3.5 Flash-Lite | 50 | 1,917 / 2,346 | 81.7% |
| 3 — Gemini 3.6 Flash | 50 | 1,907 / 2,346 | 81.3% |
| 4 — Refined hybrid | 50 | 2,016 / 2,346 | 85.9% |

The refined hybrid uses method 3 candidates for all 50 invoices and adds source-text rules. The higher-priced LLM did not outperform the lower-priced model in this run. Refinement improved the field score by 4.6 percentage points over method 3. These are in-sample results, not estimates of performance on unseen invoices.

## Deliverables

- [Short error report, comparison table and cost paragraph](REPORT.md).
- [Method 1 CSV](outputs/method1_programmatic.csv), [method 2 CSV](outputs/method2_low_cost.csv), [method 3 CSV](outputs/method3_expensive.csv), [method 4 CSV](outputs/method4_refined.csv).
- [Extraction and refinement code](methods/), [evaluation](evaluation/), [raw model responses](outputs/raw/) and [refinement provenance](outputs/method4_refinement_log.json).
- [Completed run manifest](run_manifest.json), including model IDs, package versions and input/code hashes from the executed run.
- [Original completed Colab results ZIP](runs/2026-11-06_complete/assignment3_results.zip), preserved unchanged as execution evidence.
- [Dashboard database](invoice_results.db).

Ground truth is used only for evaluation. Source filenames align predictions with the supplied PDFs. The main score compares original accounting values; the report also gives a printed-value score for the deliberately inconsistent subtotal/total amounts. Missing fields remain errors. No ground-truth values are substituted into predictions.

## Cost and reproducibility

The run used the user-selected Gemini Free Tier project. The recorded API charge is $0 conditional on that free allowance; the inference API does not independently verify billing. Standard uncached paid-equivalent estimates were $0.0887 for method 2 and $0.3851 for method 3, using rates checked on 2 November 2026. Method 4 makes no additional model calls. See the report and usage logs for token counts and timing.

The [recovery notebook](Assignment_3_Recovery_Colab.ipynb) is the source template used to finish the hosted run. The original ZIP contains an unexecuted template, not an exported executed notebook. Earlier GPU/CPU notebooks are alternative implementations and are not the source of the final scores. Earlier partial runs in `runs/` are historical checkpoints; the completed run above is authoritative.

To reproduce evaluation locally, install `pypdf>=5,<7` and `requests`, run `python scripts/setup_data.py`, then `python evaluation/compare_results.py` and `python scripts/build_report.py`. This reuses the saved predictions without API calls. To rebuild refinement, run `python methods/method4_refined.py` before evaluation.

## Dashboard

Run `npm install` and `npm start`, then open `http://localhost:3000`. The included SQLite database contains the completed results. Hosting a live website is optional.

[Assignment requirements](ASSIGNMENT_REQUIREMENTS.md).
