# Invoice Extraction Comparison Report

## Error analysis

The programmatic parser achieved 64.3% field-level accuracy (1,509 of 2,346 evaluated fields) across the 50 invoices and produced no completely exact invoice. Its most frequent errors were line-item VAT rates, unit prices and amounts, multiline descriptions and quantities, discount amounts, VAT amounts, and vendor postal codes, showing that fixed regex and line-position heuristics are brittle when invoice layouts, number formats and table structures vary. The remaining rows will be completed after the low-cost LLM, expensive LLM and refined method have been run against the same invoices and evaluated with the same ground truth.

| Method | Field accuracy | Exact invoices | Main mistakes |
|---|---:|---:|---|
| 1. Programmatic | 64.3% | 0 / 50 | Line-item VAT, unit price/amount, multiline items, discounts, VAT amount, address parsing |
| 2. Low-cost LLM | Pending | Pending | Pending evaluation |
| 3. Expensive LLM | Pending | Pending | Pending evaluation |
| 4. Refined method | Pending | Pending | Pending evaluation |

## LLM cost

Cost figures will be calculated from the actual API usage JSON written by Methods 2–4. The project records input and output tokens per invoice and `scripts/calculate_costs.py` applies the configured per-million-token rates. The final paragraph should report the actual token totals, calculated USD cost for each LLM method, and whether any free credits or account-specific limits were used. No LLM cost is stated before the API calls are actually run.
