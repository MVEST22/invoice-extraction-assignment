"""Refined hybrid: larger-model candidate plus source-text rules and arithmetic flags.
Reads candidates and PDFs only; never reads ground-truth records.
Printed values are preserved. Reconciliations are separate review flags, not repairs.
"""
from __future__ import annotations
import copy,csv,json,re
from pathlib import Path
from decimal import Decimal,InvalidOperation
from common import INVOICE_DIR,OUTPUT_DIR,ROOT,pdf_text,write_csv,unflatten,compact,normalize_number
from method1_programmatic import iso_date,COUNTRY_MAP
COUNTRIES=COUNTRY_MAP|{'Spain':'ES','Luxembourg':'LU','Ireland':'IE'}
NUM=r"-?\d[\d.,'’]*"

def money(s):
    return normalize_number(s)

def decimal(s):
    try:return Decimal(str(s))
    except (InvalidOperation,TypeError,ValueError):return None

def address(street,place):
    place=compact(place);country=None
    for name,code in COUNTRIES.items():
        if place.endswith(name):place=place[:-len(name)].rstrip(', ');country=code;break
    # UK and Dutch postcodes contain one embedded space; continental postcodes do not.
    m=re.match(r'([A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}|\d{4} ?[A-Z]{2}|\d{4,6})\s+(.+)$',place)
    return {'street':compact(street),'postal_code':m.group(1) if m else None,'city':m.group(2) if m else place},country

def refine(text,candidates):
    rec=copy.deepcopy(candidates[2] or candidates[1] or candidates[0]);flags=[];changes=[]
    lines=[compact(x) for x in text.splitlines() if compact(x)]
    def put(key,value):
        if value is not None:
            if rec.get(key)!=value:changes.append(key)
            rec[key]=value
    header=next((i for i,l in enumerate(lines) if re.search(r'(?:Invoice|Credit Note) No:',l)),None)
    if header is not None:
        h=lines[header];put('vendor',re.split(r'\s+(?:Invoice|Credit Note) No:',h)[0]);put('invoice_id',re.search(r'INV-\d{4}-\d{4}',h).group())
        if header+3<len(lines):
            street=re.split(r'\s+Date:',lines[header+1])[0]
            place=re.split(r'\s+Due:',lines[header+2])[0]+', '+lines[header+3]
            a,c=address(street,place);put('vendor_address',a);put('vendor_country',c)
        for key,label in [('date','Date'),('due_date','Due')]:
            m=re.search(r'\b'+label+r':\s*([^\n]+)',text)
            if m:put(key,iso_date(m.group(1)))
    bill=next((i for i,l in enumerate(lines) if l=='Bill to:'),None)
    if bill is not None and bill+3<len(lines):
        put('recipient',lines[bill+1]);a,c=address(lines[bill+2],lines[bill+3]);put('recipient_address',a);put('recipient_country',c)
    rates=[Decimal(v.replace(',','.'))/100 for v in re.findall(r'VAT\s*\((\d+(?:[.,]\d+)?)%\)',text)]
    if not rates:rates=[Decimal(v.replace(',','.'))/100 for v in re.findall(r'(\d+(?:[.,]\d+)?)%\s+VAT',text)]
    rates=list(dict.fromkeys(rates));rate=rates[0] if len(rates)==1 else None
    if rate is not None:put('vat_rate',str(rate))
    elif len(rates)>1:put('vat_rate','mixed');flags.append('Mixed VAT: item-level rates require review when not printed.')
    for key,pattern in [('subtotal',r'(?im)^.*?\bsubtotal\b[^\n]*'),('total',r'(?im)^.*?(?:^TOTAL:|total amount due is)[^\n]*')]:
        found=re.findall(pattern,text)
        if found:
            # Remove the label before finding the last monetary number (VAT percentages can precede it).
            nums=re.findall(NUM,found[-1]);
            if nums:put(key,money(nums[-1]))
    vatamount=[]
    for l in lines:
        if re.search(r'^VAT:|^VAT\s*\(|^Statutory VAT\s*\(.*:',l,re.I) or ('amounting to' in l and 'VAT' in l):
            nums=re.findall(NUM,l)
            if nums:vatamount.append(decimal(money(nums[-1])))
    if vatamount and all(v is not None for v in vatamount):put('vat_amount',str(sum(vatamount)))
    for key,label in [('payment_terms','Payment terms'),('bank_details','Bank')]:
        m=re.search(r'^'+label+r':\s*(.+)$',text,re.M)
        if m:put(key,compact(m.group(1)))
    put('is_credit_note','CREDIT NOTE' in text.upper())
    # Reconstruct full wrapped table descriptions instead of treating each text line as a row.
    items=[]
    if 'Description' in lines:
        i=lines.index('Description')+1
        while i<len(lines) and lines[i] in {'Qty','Unit Price','Amount','VAT','VAT Rate'}:i+=1
        description=[]
        while i<len(lines):
            line=lines[i]
            if re.search(r'^(?:The subtotal|Subtotal|Plus |All prices|Net prices|Statutory VAT|VAT|Payment terms|TOTAL)',line,re.I):break
            if re.fullmatch(NUM,line) and description and i+2<len(lines) and all(re.fullmatch(NUM,x) for x in lines[i+1:i+3]):
                items.append({'description':' '.join(description),'quantity':float(money(line)),'unit_price':money(lines[i+1]),'amount':money(lines[i+2]),'vat_rate':str(rate) if rate is not None else None});description=[];i+=3
            else:description.append(line);i+=1
    else:
        for l in lines:
            m=re.match(r'^(.*):\s*('+NUM+r')\s*×\s*(?:EUR\s*)?('+NUM+r')\s*(?:EUR)?\s*=\s*(?:EUR\s*)?('+NUM+r')\s*(?:EUR)?\.?$',l)
            if m:items.append({'description':m[1],'quantity':float(money(m[2])),'unit_price':money(m[3]),'amount':money(m[4]),'vat_rate':str(rate) if rate is not None else None});continue
            m=re.match(r'^For (.*), we invoice\s*(?:EUR\s*)?('+NUM+r')\s*(?:EUR)?\.?$',l)
            if m:items.append({'description':m[1],'quantity':1,'unit_price':money(m[2]),'amount':money(m[2]),'vat_rate':str(rate) if rate is not None else None})
    if items:
        old=rec.get('line_items') or []
        for i,item in enumerate(items):
            if item['vat_rate'] is None and i<len(old) and compact(old[i].get('description'))==item['description']:
                item['vat_rate']=old[i].get('vat_rate')
        put('line_items',items)
    # Explicit discount amounts are printed as deductions, whereas the schema uses their magnitude.
    discount_lines=[l for l in lines if re.search(r'discount|rebate per agreement|adjustment per framework',l,re.I)]
    if discount_lines:
        l=discount_lines[-1];nums=re.findall(NUM,l)
        if nums:
            amount=decimal(money(nums[-1]))
            if amount is not None:put('discount_amount',str(abs(amount)))
        pm=re.search(r'(-?\d+(?:[.,]\d+)?)%',l)
        desc='early payment discount' if 'early payment discount' in l else ('rebate per agreement' if 'rebate per agreement' in l else None)
        if desc is None:
            m=re.search(r'(adjustment per framework agreement ref\.\s*FA-[\d-]+)',l)
            desc=m[1] if m else compact(l)
        value=str(abs(Decimal(pm[1].replace(',','.')))/100) if pm else rec.get('discount_amount')
        put('discount',{'type':'percentage' if pm else 'amount','value':value,'applied_to':'subtotal','description':desc,'conditional':False})
    # No hidden correction of incorrect printed totals. Arithmetic is an audit flag only.
    amounts=[decimal(i.get('amount')) for i in rec.get('line_items',[])]
    subtotal=decimal(rec.get('subtotal'));total=decimal(rec.get('total'));vat=decimal(rec.get('vat_amount'));discount=decimal(rec.get('discount_amount')) or Decimal(0)
    if amounts and all(v is not None for v in amounts) and subtotal is not None and abs(sum(amounts)-subtotal)>Decimal('.02'):
        flags.append('Printed subtotal differs from sum of extracted line amounts (possibly VAT-inclusive prices).')
    if all(v is not None for v in [subtotal,total,vat]) and abs(subtotal+vat-discount-total)>Decimal('.02'):
        flags.append('Printed total does not reconcile: preserve printed value and review.')
    return rec,{'changed_fields':sorted(set(changes)),'review_flags':flags}

def main():
    required=['method1_programmatic.csv','method2_low_cost.csv','method3_expensive.csv'];maps=[]
    for name in required:
        with (OUTPUT_DIR/name).open(encoding='utf-8-sig',newline='') as f:
            maps.append({Path(r.get('source_file') or (r['invoice_id']+'.pdf')).stem:unflatten(r) for r in csv.DictReader(f)})
    records=[];log=[]
    for pdf in sorted(INVOICE_DIR.glob('*.pdf')):
        rec,checks=refine(pdf_text(pdf),[m.get(pdf.stem,{}) for m in maps]);rec['source_file']=pdf.name
        records.append(rec);log.append({'source_file':pdf.name,'base_candidate_method':next((i+1 for i in [2,1,0] if maps[i].get(pdf.stem)),None)}|checks)
    write_csv(records,OUTPUT_DIR/'method4_refined.csv')
    (OUTPUT_DIR/'method4_refinement_log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
    print('Refined',len(records),'invoices; no additional LLM calls or ground-truth input.')
if __name__=='__main__':main()
