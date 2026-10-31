"""Method 1: deliberately simple, fully programmatic, non-LLM parser.

It extracts text from each PDF with pypdf, then uses regex and line heuristics.
The parser is intentionally generic rather than tailored to the ground truth.
"""
from __future__ import annotations
import re
from datetime import datetime
from pathlib import Path
from common import INVOICE_DIR, OUTPUT_DIR, pdf_text, compact, normalize_number, write_csv

COUNTRY_MAP = {"Austria":"AT", "Germany":"DE", "Switzerland":"CH", "United Kingdom":"GB", "France":"FR", "Italy":"IT", "Netherlands":"NL", "Belgium":"BE"}

def iso_date(s):
    if not s: return None
    for fmt in ("%d %B %Y", "%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try: return datetime.strptime(s.strip(), fmt).date().isoformat()
        except ValueError: pass
    return s.strip()

def first(pattern, text, flags=re.I|re.M):
    m = re.search(pattern, text, flags)
    return compact(m.group(1)) if m else None

def parse_address(lines, start, stop_markers):
    out=[]
    for line in lines[start:]:
        s=compact(line)
        if not s: continue
        if any(m.lower() in s.lower() for m in stop_markers): break
        out.append(s)
        if len(out)>=4: break
    return out

def infer_country(line):
    if not line: return None
    for name, code in COUNTRY_MAP.items():
        if name.lower() in line.lower(): return code
    return None

def parse_pdf(path: Path) -> dict:
    text = pdf_text(path)
    lines = text.splitlines()
    invoice_id = first(r"(?:Invoice No|Invoice Number|Invoice|Credit Note No)\s*:?\s*(INV-\d{4}-\d{4})", text) or path.stem
    date = iso_date(first(r"\bDate\s*:?\s*([^\n]+)", text))
    due = iso_date(first(r"\bDue(?: Date)?\s*:?\s*([^\n]+)", text))

    vendor = first(r"^(.*?)\s+Invoice No\s*:", text) or first(r"^(.*?)\s+Credit Note No\s*:", text)
    vendor_address=[]
    header_idx = next((i for i,l in enumerate(lines) if vendor and vendor in l), None)
    if header_idx is not None:
        for raw in lines[header_idx+1:]:
            s=compact(raw)
            if not s: continue
            if "Bill to" in s: break
            s=re.sub(r"\s+Date\s*:.*$", "", s)
            s=re.sub(r"\s+Due\s*:.*$", "", s)
            if s: vendor_address.append(s)

    bill_idx = next((i for i,l in enumerate(lines) if "Bill to" in l), None)
    recipient=None; rec_addr=[]
    if bill_idx is not None:
        rec_addr=parse_address(lines, bill_idx+1, ["Description", "Qty", "Subtotal", "VAT"])
        if rec_addr:
            recipient=rec_addr[0]; rec_addr=rec_addr[1:]

    def split_addr(parts):
        street = parts[0] if parts else None
        postal=city=country=None
        for p in parts[1:]:
            country = country or infer_country(p)
            m=re.search(r"\b([A-Z0-9-]{4,10})\s+([^,]+)", p)
            if m: postal, city=m.group(1), m.group(2).strip()
        return street,postal,city,country
    vs,vp,vc,vco=split_addr(vendor_address)
    rs,rp,rc,rco=split_addr(rec_addr)

    currency = first(r"\b(EUR|USD|GBP|CHF|DKK)\b", text) or "EUR"
    subtotal = normalize_number(first(r"(?:subtotal(?: is)?(?:\s*:)?(?:\s*(?:EUR|USD|GBP|CHF))?\s*)([-0-9.,'’]+)", text))
    vat_m = re.search(r"VAT[^\n]*?\(?([0-9]+(?:[.,][0-9]+)?)%\)?[^\n]*?([-0-9.,'’]+)\s*(?:EUR|USD|GBP|CHF)?", text, re.I)
    vat_rate = str(float(vat_m.group(1).replace(",","."))/100) if vat_m else None
    vat_amount = normalize_number(vat_m.group(2)) if vat_m else None
    total = normalize_number(first(r"(?:TOTAL|total amount due is)\s*:?\s*(?:EUR\s*)?([-0-9.,'’]+)", text))
    if total is None:
        total = normalize_number(first(r"(?:TOTAL|total amount due is)\s*:?\s*([-0-9.,'’]+)\s*(?:EUR|USD|GBP|CHF)", text))
    discount_amount = normalize_number(first(r"(?:discount[^\n]*?\(|discount\s*:?)\s*(?:EUR\s*)?([-0-9.,'’]+)\)?", text))
    payment_terms = first(r"Payment terms\s*:\s*([^\n]+)", text)
    bank = first(r"Bank\s*:\s*([^\n]+)", text)

    items=[]
    try:
        start=next(i for i,l in enumerate(lines) if compact(l)=="Description")
    except StopIteration:
        start=-1
    if start >= 0:
        seq=[compact(x) for x in lines[start+1:] if compact(x)]
        while seq and seq[0] in {"Qty","Unit Price","Amount","VAT","VAT Rate"}: seq.pop(0)
        i=0; desc=[]
        numpat=re.compile(r"^-?[0-9][0-9.,'’]*$")
        while i < len(seq):
            if any(k in seq[i].lower() for k in ["subtotal", "statutory vat", "total amount", "payment terms", "bank:", "thank you"]): break
            if numpat.match(seq[i]) and desc:
                q=normalize_number(seq[i])
                if i+2 < len(seq) and numpat.match(seq[i+1]) and numpat.match(seq[i+2]):
                    up=normalize_number(seq[i+1]); amt=normalize_number(seq[i+2])
                    d=" ".join(desc); desc=[]
                    qty=float(q) if q and "." in q else int(q) if q else None
                    items.append({"description":d,"quantity":qty,"unit_price":up,"vat_rate":vat_rate,"amount":amt})
                    i += 3; continue
            desc.append(seq[i]); i += 1

    discount=None
    pm=re.search(r"([0-9]+(?:[.,][0-9]+)?)%\s+[^\n]*discount", text, re.I)
    if pm:
        discount={"type":"percentage","value":str(float(pm.group(1).replace(",","."))/100),"applied_to":"subtotal","description":"discount","conditional":False}
    elif discount_amount:
        discount={"type":"amount","value":discount_amount,"applied_to":"subtotal","description":"discount","conditional":False}

    return {
        "invoice_id": invoice_id, "vendor": vendor, "vendor_country": vco,
        "vendor_address":{"street":vs,"postal_code":vp,"city":vc},
        "recipient":recipient,"recipient_country":rco,
        "recipient_address":{"street":rs,"postal_code":rp,"city":rc},
        "date":date,"due_date":due,"line_items":items,"subtotal":subtotal,"vat_rate":vat_rate,"vat_amount":vat_amount,
        "discount":discount,"discount_amount":discount_amount,"total":total,"currency":currency,
        "payment_terms":payment_terms,"bank_details":bank,"is_credit_note":"CREDIT NOTE" in text.upper()
    }

def main():
    records=[parse_pdf(p) for p in sorted(INVOICE_DIR.glob("*.pdf"))]
    write_csv(records, OUTPUT_DIR/"method1_programmatic.csv")
    print(f"Wrote {len(records)} invoices to outputs/method1_programmatic.csv")

if __name__ == "__main__": main()
