from __future__ import annotations
import csv, json, re
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
INVOICE_DIR = ROOT / "invoices"
OUTPUT_DIR = ROOT / "outputs"
GROUND_TRUTH_DIR = ROOT / "ground_truth"

FIELDS = [
    "invoice_id", "vendor", "vendor_country", "vendor_street", "vendor_postal_code", "vendor_city",
    "recipient", "recipient_country", "recipient_street", "recipient_postal_code", "recipient_city",
    "date", "due_date", "line_items_json", "subtotal", "vat_rate", "vat_amount",
    "discount_json", "discount_amount", "total", "currency", "payment_terms", "bank_details",
    "is_credit_note", "source_file"
]

def pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)

def compact(s: str | None) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()

def normalize_number(s: str | None) -> str | None:
    if s is None:
        return None
    x = s.strip().replace(" ", "").replace("’", "'")
    x = re.sub(r"[^0-9,.'\-]", "", x).rstrip(".,'")
    if not x:
        return None
    if "'" in x:
        return x.replace("'", "")
    if "," in x and "." in x:
        if x.rfind(",") > x.rfind("."):
            return x.replace(".", "").replace(",", ".")
        return x.replace(",", "")
    if "," in x:
        tail = x.split(",")[-1]
        return x.replace(".", "").replace(",", ".") if len(tail) == 2 else x.replace(",", "")
    return x

def flatten(record: dict) -> dict:
    va = record.get("vendor_address") or {}
    ra = record.get("recipient_address") or {}
    return {
        "invoice_id": record.get("invoice_id"),
        "vendor": record.get("vendor"),
        "vendor_country": record.get("vendor_country"),
        "vendor_street": va.get("street"),
        "vendor_postal_code": va.get("postal_code"),
        "vendor_city": va.get("city"),
        "recipient": record.get("recipient"),
        "recipient_country": record.get("recipient_country"),
        "recipient_street": ra.get("street"),
        "recipient_postal_code": ra.get("postal_code"),
        "recipient_city": ra.get("city"),
        "date": record.get("date"),
        "due_date": record.get("due_date"),
        "line_items_json": json.dumps(record.get("line_items") or [], ensure_ascii=False, separators=(",", ":")),
        "subtotal": record.get("subtotal"),
        "vat_rate": record.get("vat_rate"),
        "vat_amount": record.get("vat_amount"),
        "discount_json": json.dumps(record.get("discount"), ensure_ascii=False, separators=(",", ":")),
        "discount_amount": record.get("discount_amount"),
        "total": record.get("total"),
        "currency": record.get("currency"),
        "payment_terms": record.get("payment_terms"),
        "bank_details": record.get("bank_details"),
        "is_credit_note": record.get("is_credit_note"),
        "source_file":record.get("source_file"),
    }

def write_csv(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in records:
            w.writerow(flatten(r))

def unflatten(row: dict) -> dict:
    def jload(v, default):
        if v in (None, "", "null", "None"): return default
        try: return json.loads(v)
        except Exception: return default
    return {
        "invoice_id": row.get("invoice_id"), "vendor": row.get("vendor"), "vendor_country": row.get("vendor_country"),
        "vendor_address":{"street":row.get("vendor_street"),"postal_code":row.get("vendor_postal_code"),"city":row.get("vendor_city")},
        "recipient":row.get("recipient"),"recipient_country":row.get("recipient_country"),
        "recipient_address":{"street":row.get("recipient_street"),"postal_code":row.get("recipient_postal_code"),"city":row.get("recipient_city")},
        "date":row.get("date"),"due_date":row.get("due_date"),"line_items":jload(row.get("line_items_json"),[]),
        "subtotal":row.get("subtotal"),"vat_rate":row.get("vat_rate"),"vat_amount":row.get("vat_amount"),
        "discount":jload(row.get("discount_json"),None),"discount_amount":row.get("discount_amount"),"total":row.get("total"),
        "currency":row.get("currency"),"payment_terms":row.get("payment_terms"),"bank_details":row.get("bank_details"),
        "is_credit_note":(None if row.get("is_credit_note") in (None,"") else str(row.get("is_credit_note")).lower() in {"true","1","yes"})
    }
