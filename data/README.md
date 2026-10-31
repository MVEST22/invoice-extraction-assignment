# Source data

Place the two assignment archives here before running the pipeline:

- `pdf.zip`
- `ground_truth.zip`

Then run:

```bash
python scripts/setup_data.py
```

The script extracts the PDFs to `invoices/` and the JSON ground truth to `ground_truth/`.

The PDF files are inputs to Methods 1–4. The JSON files are evaluation-only and must not be passed to the extraction methods.
