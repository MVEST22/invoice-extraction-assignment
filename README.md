# Invoice Extraction Lab — AI in Accounting

A P-Card-style web application for comparing four invoice-extraction methods against 50 provided ground-truth invoices.

## Assignment mapping

1. **Method 1 — Programmatic/non-LLM**: `methods/method1_programmatic.py` uses `pypdf` + regex/line heuristics.
2. **Method 2 — Low-cost LLM**: `methods/method2_low_cost.py` uses `gpt-6-luna` by default.
3. **Method 3 — More expensive LLM**: `methods/method3_expensive.py` uses `gpt-6.1-sol` by default.
4. **Method 4 — Refined**: `methods/method4_refined.py` adjudicates the first three outputs against the original invoice text, focusing on the errors found during evaluation.

Each method writes a CSV to `outputs/`. `evaluation/compare_results.py` compares available outputs with the ground truth and creates detailed and summary results. The Express dashboard reads a SQLite database produced by `scripts/build_db.py`.

## Source data

The provided source files are stored as `data/pdf.zip` and `data/ground_truth.zip`. The PDFs are the extraction inputs; the JSON files are used only after extraction for evaluation. Extract them with:

```bash
python scripts/setup_data.py
```

The extraction methods never receive the ground-truth JSON as model input.

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

This app uses an Express backend and SQLite, so **GitHub Pages alone cannot run the full application**. GitHub is used for source control; a Node-capable host is needed if you want the live dashboard online.

## Current status

Method 1 has been run on all 50 invoices and evaluated: **64.3% field-level accuracy**. Methods 2–4 require an OpenAI API key because their outputs and token costs must represent real API calls rather than fabricated results.
