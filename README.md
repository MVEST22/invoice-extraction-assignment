# Invoice Extraction Lab — AI in Accounting

A P-Card-style web application for comparing four invoice-extraction methods against 50 provided ground-truth invoices.

## Assignment mapping

1. **Method 1 — Programmatic/non-LLM**: `methods/method1_programmatic.py` uses `pypdf` + regex/line heuristics.
2. **Method 2 — Low-cost LLM**: `methods/method2_low_cost.py` uses `gpt-6-luna` by default.
3. **Method 3 — More expensive LLM**: `methods/method3_expensive.py` uses `gpt-6.1-sol` by default.
4. **Method 4 — Refined**: `methods/method4_refined.py` adjudicates the first three outputs against the original invoice text, focusing on the errors found during evaluation.

The model choices and standard API rates were verified against OpenAI's current API documentation on 31 October 2026.

## Source data

The assignment provides two source archives:

- `pdf.zip` → the 50 invoice PDFs used as extraction input.
- `ground_truth.zip` → the 50 JSON ground-truth records used **only for evaluation after extraction**.

The GitHub connector used to build this repository can write text/code files but cannot transfer the binary source archives from the working environment. Place the two supplied ZIP files in a local `data/` folder and run:

```bash
python scripts/setup_data.py
```

This creates `invoices/` and `ground_truth/`. The extraction methods never receive ground-truth JSON as model input.

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
npm install
```

Copy `.env.example` to `.env` and add your OpenAI API key:

```text
OPENAI_API_KEY=...
LOW_COST_MODEL=gpt-6-luna
EXPENSIVE_MODEL=gpt-6.1-sol
```

Never commit `.env` to GitHub.

## Run the four methods

```bash
python methods/method1_programmatic.py
python methods/method2_low_cost.py
python methods/method3_expensive.py
python methods/method4_refined.py
```

Each method writes its required CSV to `outputs/`.

Then evaluate and rebuild the dashboard database:

```bash
python evaluation/compare_results.py
python scripts/calculate_costs.py
python scripts/build_db.py
```

## Start the dashboard

```bash
npm start
```

Open `http://localhost:3000`.

The dashboard uses an Express backend and SQLite, so GitHub Pages alone cannot run the full application. GitHub is used for source control; a Node-capable host is needed for a live deployment.

## Current status

Method 1 has been run locally on all 50 invoices and evaluated at **64.3% field-level accuracy (1,509 / 2,346 fields correct)**. Its most frequent errors are line-item VAT rates, unit prices/amounts, multiline descriptions/quantities, discounts, VAT amounts, and vendor postal codes. Methods 2–4 still require an actual `OPENAI_API_KEY` so the submitted CSVs and token-cost figures come from genuine API calls rather than fabricated results.
