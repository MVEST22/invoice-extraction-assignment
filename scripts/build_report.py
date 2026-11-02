"""Build the requested one-paragraph, one-table error report plus one cost paragraph."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
summary=json.loads((ROOT/'evaluation/summary.json').read_text());costs=json.loads((ROOT/'evaluation/costs.json').read_text())
complete=len(summary)==4 and all(r['prediction_rows']==50 for r in summary)
models={r['method']:r['model'] for r in costs}
lines=['# Assignment 3 - invoice extraction comparison','']
lines.append(('All four methods processed 50 invoices.' if complete else 'INCOMPLETE RUN: not all four methods have 50 results.')+' The rule-based baseline, two local LLMs (identified in the table), and refined hybrid are compared below. The hybrid applies source-text rules for wrapped line items, addresses, VAT and discounts to the larger-model candidate, and flags arithmetic differences without rewriting printed amounts. Errors are measured by exact normalized leaf-field comparison, including list lengths; absent or invalid LLM fields remain errors. The supplied ground truth includes corrected amounts and printed amounts: the main score uses its original accounting values, while the printed-value score substitutes only rendered subtotal/total. Therefore some main-score errors describe deliberate invoice inconsistencies. The refinement was developed on this assignment data, so these are descriptive in-sample results, not evidence of performance on unseen invoices.')
lines+=['','| Method | Rows | Correct / fields | Field score | Printed-value score | Main error fields |','|---|---:|---:|---:|---:|---|']
names={'method1':'1: non-LLM rules','method2':'2: '+models.get('method2_low_cost','pending'),'method3':'3: '+models.get('method3_expensive','pending'),'method4':'4: refined hybrid'}
for r in summary:
 errors='; '.join(f'{k} ({v})' for k,v in r['top_error_fields'][:4]) or 'None'
 lines.append(f"| {names[r['method']]} | {r['prediction_rows']} | {r['field_correct']} / {r['field_total']} | {r['field_accuracy']:.1%} | {r['printed_field_accuracy']:.1%} | {errors} |")
lines+=['','## LLM cost paragraph','']
usage='; '.join(f"{r['model']}: {r['input_tokens']:,} input and {r['output_tokens']:,} output tokens, {r['generation_seconds']/60:.1f} generation minutes, {r['parse_failures']} JSON parse failures" for r in costs)
lines.append('Actual API spending was $0: both open models ran locally on the Colab runtime without an API key, free-tier API credits or per-token fees. '+usage+'. Method 4 reused those outputs and added deterministic checks, with no further LLM calls. Method 3 uses the larger model for the active hardware profile, not a purchased API tier. GPU mode uses 1.5B and 7B (4-bit); CPU mode uses 0.5B and 1.5B (float32). Quantization and hardware affect resource use and possibly accuracy, so measured runtime is reported rather than an assumed price ratio. Free Colab sessions are availability- and quota-limited and may disconnect; this experiment does not establish a commercial dollar cost per invoice. If “more expensive LLM” must specifically mean a higher-priced hosted API, this free-compute comparison is a disclosed substitution, not proof that such a paid service was used.')
(ROOT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('REPORT.md generated; complete:',complete)
