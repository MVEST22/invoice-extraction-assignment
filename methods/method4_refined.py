"""Method 4: refined adjudication method.

Runs after methods 1-3. It gives a strong model the source invoice text plus the three
candidate extractions and asks it to resolve disagreements, explicitly focusing on the
error types observed in evaluation: locale number formats, multiline line items, VAT,
discounts, addresses, credit notes, and preserving printed-but-inconsistent totals.
"""
from __future__ import annotations
import csv, json, os, sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from common import ROOT, INVOICE_DIR, OUTPUT_DIR, pdf_text, unflatten, write_csv
from llm_extract import SCHEMA

load_dotenv(ROOT/".env")
MODEL=os.getenv("EXPENSIVE_MODEL","gpt-6.1-sol")

PROMPT="""You are the final invoice extraction adjudicator. Use the SOURCE INVOICE as authority.
Three earlier methods are included only as candidates and can be wrong.
Resolve every field carefully. Pay special attention to:
1) English, German and Swiss number separators; 2) multiline descriptions and table cells;
3) VAT shown as a rate, amount, mixed VAT, reverse charge, or implicit wording;
4) percentage, fixed-amount and trade-term discounts; 5) vendor/recipient address boundaries;
6) credit notes and negative values; 7) printed subtotal/total inconsistencies.
Do NOT repair invoice arithmetic. Return what is actually printed, normalized to the schema.
Dates: YYYY-MM-DD. Country: ISO alpha-2. Numeric strings: decimal point, no thousands separators.
Percentages: decimal fractions (20% = 0.20)."""

def load_csv(name):
    with open(OUTPUT_DIR/name,encoding="utf-8-sig",newline="") as f:
        return {r["invoice_id"]:unflatten(r) for r in csv.DictReader(f)}

def main():
    required=["method1_programmatic.csv","method2_low_cost.csv","method3_expensive.csv"]
    missing=[x for x in required if not (OUTPUT_DIR/x).exists()]
    if missing: raise SystemExit("Run Methods 1-3 first. Missing: "+", ".join(missing))
    candidates=[load_csv(x) for x in required]
    client=OpenAI(); records=[]; usage=[]
    for pdf in sorted(INVOICE_DIR.glob("*.pdf")):
        iid=pdf.stem
        payload={"source_invoice_text":pdf_text(pdf),"method1":candidates[0].get(iid),"method2":candidates[1].get(iid),"method3":candidates[2].get(iid)}
        resp=client.responses.create(model=MODEL,
          input=[{"role":"system","content":PROMPT},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],
          text={"format":{"type":"json_schema","name":"invoice","strict":True,"schema":SCHEMA}},
          reasoning={"effort":"medium"})
        records.append(json.loads(resp.output_text))
        u=resp.usage;usage.append({"invoice_id":iid,"input_tokens":getattr(u,"input_tokens",0),"output_tokens":getattr(u,"output_tokens",0),"total_tokens":getattr(u,"total_tokens",0)})
        print("refined:",iid)
    write_csv(records,OUTPUT_DIR/"method4_refined.csv")
    (OUTPUT_DIR/"method4_refined_usage.json").write_text(json.dumps(usage,indent=2),encoding="utf-8")

if __name__=="__main__": main()
