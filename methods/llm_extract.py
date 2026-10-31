"""Shared LLM extraction engine for Methods 2 and 3.
Uses extracted PDF text and Structured Outputs. No ground truth is provided to the model.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from common import INVOICE_DIR, OUTPUT_DIR, pdf_text, write_csv

load_dotenv(Path(__file__).resolve().parents[1]/".env")

SCHEMA = {
  "type":"object","additionalProperties":False,"properties":{
    "invoice_id":{"type":["string","null"]},"vendor":{"type":["string","null"]},"vendor_country":{"type":["string","null"]},
    "vendor_address":{"type":"object","additionalProperties":False,"properties":{"street":{"type":["string","null"]},"postal_code":{"type":["string","null"]},"city":{"type":["string","null"]}},"required":["street","postal_code","city"]},
    "recipient":{"type":["string","null"]},"recipient_country":{"type":["string","null"]},
    "recipient_address":{"type":"object","additionalProperties":False,"properties":{"street":{"type":["string","null"]},"postal_code":{"type":["string","null"]},"city":{"type":["string","null"]}},"required":["street","postal_code","city"]},
    "date":{"type":["string","null"]},"due_date":{"type":["string","null"]},
    "line_items":{"type":"array","items":{"type":"object","additionalProperties":False,"properties":{"description":{"type":"string"},"quantity":{"type":["number","null"]},"unit_price":{"type":["string","null"]},"vat_rate":{"type":["string","null"]},"amount":{"type":["string","null"]}},"required":["description","quantity","unit_price","vat_rate","amount"]}},
    "subtotal":{"type":["string","null"]},"vat_rate":{"type":["string","null"]},"vat_amount":{"type":["string","null"]},
    "discount":{"type":["object","null"],"additionalProperties":False,"properties":{"type":{"type":["string","null"]},"value":{"type":["string","null"]},"applied_to":{"type":["string","null"]},"description":{"type":["string","null"]},"conditional":{"type":["boolean","null"]}},"required":["type","value","applied_to","description","conditional"]},
    "discount_amount":{"type":["string","null"]},"total":{"type":["string","null"]},"currency":{"type":["string","null"]},"payment_terms":{"type":["string","null"]},"bank_details":{"type":["string","null"]},"is_credit_note":{"type":"boolean"}
  },"required":["invoice_id","vendor","vendor_country","vendor_address","recipient","recipient_country","recipient_address","date","due_date","line_items","subtotal","vat_rate","vat_amount","discount","discount_amount","total","currency","payment_terms","bank_details","is_credit_note"]
}

SYSTEM = """Extract invoice data exactly as printed. Return ISO dates (YYYY-MM-DD), ISO-3166 alpha-2 country codes, decimal numbers as strings with a dot and no thousands separators, VAT/discount percentages as decimal fractions (20% -> 0.20), and preserve full line-item descriptions. Do not repair arithmetic inconsistencies: capture the values printed on the invoice."""

def extract(client, model, text):
    resp=client.responses.create(
        model=model,
        input=[{"role":"system","content":SYSTEM},{"role":"user","content":text}],
        text={"format":{"type":"json_schema","name":"invoice","strict":True,"schema":SCHEMA}},
        reasoning={"effort":"low"}
    )
    return json.loads(resp.output_text), resp.usage

def main():
    if len(sys.argv)<3:
        raise SystemExit("Usage: python methods/llm_extract.py <model> <output.csv> [usage.json]")
    model=sys.argv[1]; outfile=OUTPUT_DIR/sys.argv[2]; usagefile=OUTPUT_DIR/(sys.argv[3] if len(sys.argv)>3 else sys.argv[2].replace('.csv','_usage.json'))
    client=OpenAI()
    records=[]; usage=[]
    for p in sorted(INVOICE_DIR.glob("*.pdf")):
        rec,u=extract(client,model,pdf_text(p)); records.append(rec)
        usage.append({"invoice_id":p.stem,"input_tokens":getattr(u,"input_tokens",0),"output_tokens":getattr(u,"output_tokens",0),"total_tokens":getattr(u,"total_tokens",0)})
        print(f"{model}: {p.name}")
    write_csv(records,outfile)
    usagefile.write_text(json.dumps(usage,indent=2),encoding="utf-8")

if __name__=="__main__": main()
