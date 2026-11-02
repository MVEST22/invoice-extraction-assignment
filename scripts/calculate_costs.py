"""Measured usage and clearly separate free-tier charges from standard-price estimates."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for method in ['method2_low_cost','method3_expensive']:
 p=ROOT/'outputs'/(method+'_usage.json')
 if not p.exists():continue
 usage=json.loads(p.read_text());hosted=bool(usage and usage[0].get('provider')=='Gemini API')
 inp=sum(x.get('input_tokens',0) for x in usage);out=sum(x.get('output_tokens',0) for x in usage);thinking=sum(x.get('thinking_tokens',0) for x in usage)
 estimate=sum((x.get('input_tokens',0)*x.get('standard_paid_rate_input_per_m',0)+(x.get('output_tokens',0)+x.get('thinking_tokens',0))*x.get('standard_paid_rate_output_per_m',0))/1e6 for x in usage) if hosted else None
 rows.append({'method':method,'model':usage[0]['model'] if usage else None,'provider':'Gemini API' if hosted else 'local open weights',
  'input_tokens':inp,'output_tokens':out,'thinking_tokens':thinking,'generation_seconds':sum(x.get('request_seconds',x.get('generation_seconds',0)) for x in usage),
  'actual_api_cost_usd_on_free_tier':0,'standard_uncached_equivalent_usd':estimate,
  'invoices':sum(len(x['source_files']) if 'source_files' in x else 1 for x in usage),
  'requests':len(usage) if hosted else 0,'parse_failures':sum(x.get('parse_failures',int(x.get('status','').startswith('parse_failure'))) for x in usage),
  'billing':'Zero only for user-selected eligible Free Tier project; no billing enabled. Billing status is not independently checked by this API.' if hosted else 'No API calls or token charges; local compute only.'})
(ROOT/'evaluation'/'costs.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
