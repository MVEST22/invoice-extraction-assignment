# Assignment 3 - Invoice Extraction Lab

Compare four extraction methods on the supplied 50 invoice PDFs. Ground-truth JSON is used only after extraction to evaluate results.

## Recommended now: Gemini in Colab, without a GPU

Open [Assignment_3_Gemini_Colab.ipynb](https://colab.research.google.com/github/MVEST22/invoice-extraction-assignment/blob/main/Assignment_3_Gemini_Colab.ipynb), select **CPU**, and choose **Run all**. Enter your key from a **Free Tier Google AI Studio project with billing disabled** only in the private prompt. No local model downloads or GPU access are needed. Do not paste the key into source, chat or GitHub.

This uses Gemini Flash-Lite for Method 2 and the higher-standard-price Gemini Flash for Method 3, then the same source-only hybrid refinement. It selects only documented free-tier model IDs that your key lists as available: preferred pair 3.5 Flash-Lite and 3.8 Flash, with 3.1 Flash-Lite or 3.6 Flash as allowlisted alternatives. The actual selected models and returned versions are saved. Model-list access does not verify project billing status: using your unbilled Free Tier project is essential. Standard rates checked on 2 November 2026 are recorded separately from free-tier charges. Both model tiers may use the free allowance; no paid credits need to be purchased.

Five source invoices are grouped in each synchronous request (not the paid asynchronous Batch API). Ten successful generation requests per model cover all 50 invoices. Raw responses and checkpoints are saved immediately. An unresolved quota/access error stops the run instead of upgrading. Runtime depends on quotas and service latency; a fixed completion time is not promised. Google free-tier data-use terms apply to the submitted source text. Ground-truth JSON is never sent to Gemini.

The final cell downloads `assignment3_results.zip`; also download the executed notebook. The returned checkpoint confirms 50 genuine Flash-Lite results and five Flash results; the run is still incomplete. No Gemini results or costs have been invented. The report and dashboard database are rebuilt after a successful real run. Do not mix this with an earlier local-model run.

## GPU quota reached? Slower local CPU alternative

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
- A returned Gemini checkpoint verifies Method 2 completed all 50 invoices: **1,917 / 2,346 fields (81.7%)**. Method 3 has only five saved invoices; Method 4 has not run. See `REPORT.md` and `runs/2026-11-02_partial/`. No missing LLM outputs or scores are fabricated.
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

## Preserved partial run

The original user-returned ZIP is saved as `runs/2026-11-02_partial/checkpoint.zip`, with directly readable CSVs, usage logs and manifest beside it. All 50 source PDF hashes match the supplied input archive. Method 2's 81.7% score was independently reproduced locally. The ZIP preserves the original, outdated report template as evidence; use the repository root `REPORT.md` for the verified interim summary. The overall 9.8% shown for Method 3 by the checkpoint's evaluator includes 45 missing invoices and must not be presented as its accuracy on a completed 50-invoice run. More results and the actual executed notebook are still needed.
