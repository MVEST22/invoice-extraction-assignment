from __future__ import annotations
import csv,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"invoice_results.db"
if DB.exists(): DB.unlink()
con=sqlite3.connect(DB); cur=con.cursor()
cur.executescript('''
CREATE TABLE invoices(invoice_id TEXT PRIMARY KEY, ground_truth_json TEXT NOT NULL);
CREATE TABLE results(method TEXT NOT NULL, invoice_id TEXT NOT NULL, result_json TEXT NOT NULL, accuracy REAL, error_count INTEGER, PRIMARY KEY(method,invoice_id));
CREATE TABLE summary(method TEXT PRIMARY KEY, invoices INTEGER, exact_invoices INTEGER, field_correct INTEGER, field_total INTEGER, field_accuracy REAL, top_error_fields_json TEXT);
''')
for p in sorted((ROOT/"ground_truth").glob("*.json")):
    cur.execute("INSERT INTO invoices VALUES (?,?)",(p.stem,p.read_text(encoding="utf-8")))
details={}
dp=ROOT/"evaluation"/"details.json"
if dp.exists():
    for d in json.loads(dp.read_text(encoding="utf-8")): details[(d['method'],d['invoice_id'])]=d
methods={"method1":"method1_programmatic.csv","method2":"method2_low_cost.csv","method3":"method3_expensive.csv","method4":"method4_refined.csv"}
for method,fn in methods.items():
    p=ROOT/"outputs"/fn
    if not p.exists(): continue
    with p.open(encoding="utf-8-sig",newline="") as f:
        for row in csv.DictReader(f):
            d=details.get((method,row['invoice_id']),{})
            cur.execute("INSERT INTO results VALUES (?,?,?,?,?)",(method,row['invoice_id'],json.dumps(row,ensure_ascii=False),d.get('accuracy'),len(d.get('errors',[]))))
sp=ROOT/"evaluation"/"summary.json"
if sp.exists():
    for s in json.loads(sp.read_text(encoding="utf-8")):
        cur.execute("INSERT INTO summary VALUES (?,?,?,?,?,?,?)",(s['method'],s['invoices'],s['exact_invoices'],s['field_correct'],s['field_total'],s['field_accuracy'],json.dumps(s['top_error_fields'],ensure_ascii=False)))
con.commit();con.close();print(DB)
