from __future__ import annotations
import csv, json, re
from decimal import Decimal, InvalidOperation
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"methods"))
from common import GROUND_TRUTH_DIR, OUTPUT_DIR, unflatten

METHODS={
 "method1":"method1_programmatic.csv",
 "method2":"method2_low_cost.csv",
 "method3":"method3_expensive.csv",
 "method4":"method4_refined.csv",
}
IGNORE_GT={"variants","rendered_subtotal","rendered_total","error_note"}
NUMERIC_NAMES={"quantity","unit_price","vat_rate","amount","subtotal","vat_amount","discount_amount","total","value"}

def norm_text(v):
    if v is None: return None
    return re.sub(r"\s+"," ",str(v)).strip().rstrip(".")

def numeq(a,b):
    try: return Decimal(str(a))==Decimal(str(b))
    except (InvalidOperation,ValueError,TypeError): return False

def eq(path,a,b):
    name=path.split(".")[-1]
    if a is None and b in (None,""): return True
    if b is None and a in (None,""): return True
    if name in NUMERIC_NAMES and a not in (None,"") and b not in (None,""):
        return numeq(a,b)
    if isinstance(a,bool) or isinstance(b,bool): return bool(a)==bool(b)
    return norm_text(a)==norm_text(b)

def flatten_compare(obj,prefix=""):
    out={}
    if isinstance(obj,dict):
        for k,v in obj.items():
            if not prefix and k in IGNORE_GT: continue
            key=f"{prefix}.{k}" if prefix else k
            out.update(flatten_compare(v,key))
    elif isinstance(obj,list):
        for i,v in enumerate(obj): out.update(flatten_compare(v,f"{prefix}[{i}]"))
        out[f"{prefix}.__length__"]=len(obj)
    else: out[prefix]=obj
    return out

def read_method(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return {r["invoice_id"]:unflatten(r) for r in csv.DictReader(f)}

def main():
    truths={p.stem:json.loads(p.read_text(encoding="utf-8")) for p in sorted(GROUND_TRUTH_DIR.glob("*.json"))}
    details=[]; summary=[]
    for method,filename in METHODS.items():
        path=OUTPUT_DIR/filename
        if not path.exists(): continue
        preds=read_method(path)
        total=correct=0; invoices_exact=0; err_counts={}
        for iid,gt in truths.items():
            pred=preds.get(iid,{})
            g=flatten_compare(gt); p=flatten_compare(pred)
            errors=[]
            for key,gv in g.items():
                pv=p.get(key)
                ok=eq(key,gv,pv)
                total+=1; correct+=int(ok)
                if not ok:
                    errors.append({"field":key,"expected":gv,"actual":pv})
                    base=re.sub(r"\[\d+\]","[]",key)
                    err_counts[base]=err_counts.get(base,0)+1
            invoices_exact += int(not errors)
            details.append({"method":method,"invoice_id":iid,"correct_fields":len(g)-len(errors),"total_fields":len(g),"accuracy":(len(g)-len(errors))/len(g),"errors":errors})
        summary.append({"method":method,"invoices":len(truths),"exact_invoices":invoices_exact,"field_correct":correct,"field_total":total,"field_accuracy":correct/total if total else 0,"top_error_fields":sorted(err_counts.items(),key=lambda x:x[1],reverse=True)[:8]})
    (ROOT/"evaluation"/"details.json").write_text(json.dumps(details,ensure_ascii=False,indent=2),encoding="utf-8")
    (ROOT/"evaluation"/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    with (ROOT/"evaluation"/"summary.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=["method","invoices","exact_invoices","field_correct","field_total","field_accuracy","top_error_fields"]);w.writeheader()
        for r in summary:
            x=r.copy();x["top_error_fields"]=json.dumps(x["top_error_fields"],ensure_ascii=False);w.writerow(x)
    for r in summary: print(r["method"],f"field accuracy {r['field_accuracy']:.1%}","exact invoices",r["exact_invoices"])

if __name__=="__main__": main()
