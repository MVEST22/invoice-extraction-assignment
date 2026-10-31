from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# Standard short-context rates per 1M tokens. Update if pricing changes.
RATES={
 "method2_low_cost_usage.json":{"model":"gpt-6-luna","input_per_m":0.10,"output_per_m":0.50},
 "method3_expensive_usage.json":{"model":"gpt-6.1-sol","input_per_m":2.00,"output_per_m":10.00},
 "method4_refined_usage.json":{"model":"gpt-6.1-sol","input_per_m":2.00,"output_per_m":10.00},
}
rows=[]
for fn,rate in RATES.items():
 p=ROOT/"outputs"/fn
 if not p.exists(): continue
 usage=json.loads(p.read_text(encoding="utf-8")); inp=sum(x.get("input_tokens",0) for x in usage); out=sum(x.get("output_tokens",0) for x in usage)
 cost=inp/1e6*rate["input_per_m"]+out/1e6*rate["output_per_m"]
 rows.append({"method":fn.replace('_usage.json',''),"model":rate['model'],"input_tokens":inp,"output_tokens":out,"estimated_usd":round(cost,6)})
print(json.dumps(rows,indent=2))
(ROOT/"evaluation"/"costs.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
