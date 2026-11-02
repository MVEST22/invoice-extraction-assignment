"""Build the requested one-paragraph, one-table error report plus one cost paragraph."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
summary=json.loads((ROOT/'evaluation/summary.json').read_text());costs=json.loads((ROOT/'evaluation/costs.json').read_text())
complete=len(summary)==4 and all(r['prediction_rows']==50 for r in summary)
models={r['method']:r['model'] for r in costs}
lines=['# Assignment 3 - invoice extraction comparison','']
lines.append(('All four methods processed 50 invoices.' if complete else 'INCOMPLETE RUN: not all four methods have 50 results.')+' The rule-based baseline, two LLMs (identified in the table), and refined hybrid are compared below. The hybrid applies source-text rules for wrapped line items, addresses, VAT and discounts to the larger-model candidate, and flags arithmetic differences without rewriting printed amounts. Errors are measured by exact normalized leaf-field comparison, including list lengths; absent or invalid LLM fields remain errors. The supplied ground truth includes corrected amounts and printed amounts: the main score uses its original accounting values, while the printed-value score substitutes only rendered subtotal/total. Therefore some main-score errors describe deliberate invoice inconsistencies. The refinement was developed on this assignment data, so these are descriptive in-sample results, not evidence of performance on unseen invoices.')
logpath=ROOT/'outputs/method4_refinement_log.json'
if logpath.exists():
    log=json.loads(logpath.read_text());counts={str(i):sum(r.get('base_candidate_method')==i for r in log) for i in (1,2,3)}
    lines[-1]+=' Refinement base candidates: method 1 for '+counts['1'].__str__()+' invoices, method 2 for '+counts['2'].__str__()+' and method 3 for '+counts['3'].__str__()+'. When method 3 is incomplete this hybrid result is provisional and will be regenerated after completion.'
lines+=['','| Method | Rows | Correct / fields | Field score | Printed-value score | Main error fields |','|---|---:|---:|---:|---:|---|']
names={'method1':'1: non-LLM rules','method2':'2: '+models.get('method2_low_cost','pending'),'method3':'3: '+models.get('method3_expensive','pending'),'method4':'4: refined hybrid'}
for r in summary:
 errors='; '.join(f'{k} ({v})' for k,v in r['top_error_fields'][:4]) or 'None'
 if r['prediction_rows']<50:
  lines.append(f"| {names[r['method']]} | {r['prediction_rows']} | Pending full run | Pending | Pending | Incomplete coverage; missing invoices are not ordinary extraction errors |")
  continue
 lines.append(f"| {names[r['method']]} | {r['prediction_rows']} | {r['field_correct']} / {r['field_total']} | {r['field_accuracy']:.1%} | {r['printed_field_accuracy']:.1%} | {errors} |")
lines+=['','## LLM cost paragraph','']
usage='; '.join(f"{r['model']}: {r['input_tokens']:,} input and {r['output_tokens']:,} output tokens and {r.get('thinking_tokens',0):,} thinking tokens, {r['generation_seconds']/60:.1f} recorded minutes, {r['parse_failures']} JSON parse failures" for r in costs)
if any(r.get('provider')=='Gemini API' for r in costs):
 estimates='; '.join(f"{r['model']}: standard uncached-equivalent estimate ${r['standard_uncached_equivalent_usd']:.4f}" for r in costs if r.get('standard_uncached_equivalent_usd') is not None)
 lines.append('The hosted Gemini run uses a lower-priced Flash-Lite model and a higher-priced Flash model through the user-selected Free Tier project, without enabling billing. Under that free allowance the API charge is $0; billing status is not independently verified by the inference API. '+usage+'. '+estimates+'. Estimates use the published standard rates checked on 2 November 2026, include separately reported thinking tokens, and are not invoices or actual charges; implicit caching, pricing changes and server-side routing may affect commercial billing. No promotional paid credits were purchased. Free access is subject to model/project eligibility and request/token quotas, and the notebook stops on an unresolved limit instead of upgrading or choosing a paid-only model. Method 4 reuses predictions and makes no additional LLM calls. Raw responses preserve the requested model and returned model version.')
else:
 lines.append('Both open models ran locally without API fees. '+usage+'. The GPU profile compares Qwen 1.5B with 7B (4-bit); the CPU profile compares 0.5B with 1.5B (float32). These are higher-compute alternatives, not purchased price tiers. Method 4 adds no LLM call. Free Colab session limits still apply.')

(ROOT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('REPORT.md generated; complete:',complete)
