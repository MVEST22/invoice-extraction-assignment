"""Report measured local inference usage; never invent a commercial token tariff."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for method in ['method2_low_cost','method3_expensive']:
 p=ROOT/'outputs'/(method+'_usage.json')
 if not p.exists():continue
 usage=json.loads(p.read_text());rows.append({'method':method,'model':usage[0]['model'] if usage else None,
  'input_tokens':sum(x.get('input_tokens',0) for x in usage),'output_tokens':sum(x.get('output_tokens',0) for x in usage),
  'generation_seconds':sum(x.get('generation_seconds',0) for x in usage),'actual_api_cost_usd':0,
  'invoices':len(usage),'parse_failures':sum(x.get('status','').startswith('parse_failure') for x in usage),
  'billing':'Local open weights on supplied compute; no API calls or token charges. Colab free GPU availability is not guaranteed.'})
(ROOT/'evaluation'/'costs.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
