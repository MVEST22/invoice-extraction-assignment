"""Regression checks that do not run an LLM or read ground truth into extraction."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'methods'))
from local_llm import parse_response
from method4_refined import address,refine
assert parse_response('```json\n{"vendor":"Example","line_items":[],"total":"12.00"}\n```')['total']=='12.00'
for s in ['!!!','{"boxes": []}','{"vendor": "x", "line_items": [1]}']:
 try:parse_response(s)
 except ValueError:pass
 else:raise AssertionError('Accepted malformed invoice response')
a,c=address('1 Main Road','EC2R 6AA London, United Kingdom');assert a['postal_code']=='EC2R 6AA' and a['city']=='London' and c=='GB'
a,c=address('2 Gracht','1017 BP Amsterdam, Netherlands');assert a['postal_code']=='1017 BP' and c=='NL'
text='''INVOICE
Example GmbH Invoice No: INV-2026-9999
One Road Date: 1 March 2026
1010 Wien Due: 31 March 2026
Austria
Description
Qty
Unit Price
Amount
A wrapped long
service description
2
1.234,50
2.469,00
Subtotal: 2.469,00 EUR
VAT (20%): 493,80 EUR
TOTAL: 9.999,00 EUR
'''
r,log=refine(text,[{}, {}, {}]);assert r['line_items'][0]['description']=='A wrapped long service description';assert r['line_items'][0]['amount']=='2469.00';assert r['total']=='9999.00';assert log['review_flags']
print('Passed JSON failure handling, postcode parsing, wrapped descriptions and printed-total preservation checks.')

import importlib.util
spec=importlib.util.spec_from_file_location("scoring",Path(__file__).parent/"evaluation/compare_results.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
assert not mod.eq("discount.conditional",False,None)
assert mod.eq("total","1234.50","1234.5")
print("Passed strict missing-boolean and decimal-equivalence scoring checks.")
