# Assignment 3 - Invoice Extraction Lab

Compare four extraction methods on the supplied 50 invoice PDFs. Ground-truth JSON is used only after extraction to evaluate results.

## GPU quota reached? Use the CPU version

Open [Assignment_3_CPU_Colab.ipynb](https://colab.research.google.com/github/MVEST22/invoice-extraction-assignment/blob/main/Assignment_3_CPU_Colab.ipynb) and select **CPU**, then **Run all**. It uses Qwen2.5-0.5B and Qwen2.5-1.5B in float32; no GPU, API key or payment is required. This changes the models being compared and the report records their actual names. CPU inference may take several hours; free-session limits still apply. Keep the runtime active and download results before disconnecting. This is a new, unexecuted path until actual CPU results are returned.

## Run without paid APIs

Open [Assignment_3_Free_Colab.ipynb in Colab](https://colab.research.google.com/github/MVEST22/invoice-extraction-assignment/blob/main/Assignment_3_Free_Colab.ipynb), choose **Runtime > Change runtime type > T4 GPU**, then **Runtime > Run all**. No code editing, API key, or purchase is required. Free GPU availability is not guaranteed. Stop if Colab asks you to purchase compute.

The notebook downloads this repository and unpacks the two existing source archives in `data/`. It runs:

1. **Non-LLM baseline:** pypdf text extraction and simple rules.
2. **Smaller LLM:** Qwen2.5-1.5B-Instruct, half precision.
3. **Larger LLM:** Qwen2.5-7B-Instruct, 4-bit quantization.
4. **Refined hybrid:** larger-model candidate plus source-text rules for wrapped descriptions, addresses, VAT and discounts; arithmetic differences are flagged, not silently corrected.

The larger model is a higher-compute alternative, **not a paid API tier**. Both have $0 API fees. If the lecturer interprets “more expensive LLM” specifically as a more expensive hosted service, the open-model comparison is a disclosed substitution and needs the lecturer's acceptance. Parameter count and quantization do not establish a monetary cost ratio; actual token counts and generation time are recorded.

The final cell downloads `assignment3_results.zip`. Also download the executed notebook with **File > Download > Download .ipynb**. Return both for final review. Per-invoice raw answers and checkpoints are retained, so rerunning the same notebook in the same active runtime reuses completed outputs. Do not reset the runtime before downloading the results. Model downloads and 100 invoice extractions can take substantial time.

## Current verified status

- Method 1 executed on all 50 uploaded invoices: **1,496 / 2,346 fields (63.8%)** against the original ground-truth accounting values; 0 fully exact invoices.
- Methods 2, 3 and 4 have code prepared, but **their real Colab run is still required**. No LLM CSV or scores are fabricated.
- The parser/refinement regression checks pass locally. GPU inference has not been tested in this workspace.
- The old API-only methods are no longer the default. `methods/llm_extract.py` remains legacy reference code and is not invoked by the free notebook; its hosted API path has not been run.

## Deliverables

The Colab result ZIP contains all four `outputs/method*.csv` files (one row per source PDF, with nested line items stored as JSON), code, raw model answers, usage and refinement logs, evaluation details, `REPORT.md`, and the dashboard SQLite database. The report has one errors paragraph, one comparison table and one cost paragraph. Source PDF names anchor evaluation even when an LLM misreads the invoice number. Invalid model responses stay recorded as failures and score as missing fields; they are not replaced with answers from ground truth.

Some invoices deliberately print incorrect subtotal or total amounts. The primary score uses the original ground-truth values; a second score substitutes the supplied `rendered_subtotal` and `rendered_total` solely for evaluating faithful extraction. This distinction is explicit in the report. No ground-truth corrections are fed into extraction or refinement.

## Dashboard and local use

The existing Express/SQLite dashboard is retained. After a completed run, copy `outputs/`, `evaluation/` and `invoice_results.db` from the results ZIP into this project; run `npm install` and `npm start`, then open `http://localhost:3000`. A live website is optional; the assignment requires CSVs, code and the short report.

For a local CUDA machine: install `requirements.txt` plus compatible PyTorch, run `python scripts/setup_data.py`, then `python run_pipeline.py`. The old GitHub Actions API workflow is replaced with a CPU baseline check; it does not call paid services.

## Sources

- [Assignment requirements](ASSIGNMENT_REQUIREMENTS.md).
- [Qwen 1.5B model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct).
- [Qwen 7B model card](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct).
- [Hugging Face bitsandbytes documentation](https://huggingface.co/docs/transformers/quantization/bitsandbytes).

Models and model cards are external dependencies. The notebook records package versions and file hashes; model revisions are also recorded when available.
