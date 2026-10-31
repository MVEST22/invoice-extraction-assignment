from pathlib import Path
import os, sys, json
from dotenv import load_dotenv
ROOT=Path(__file__).resolve().parents[1]
load_dotenv(ROOT/'.env')
checks={
  'invoices': len(list((ROOT/'invoices').glob('*.pdf'))),
  'ground_truth': len(list((ROOT/'ground_truth').glob('*.json'))),
  'method1_output': (ROOT/'outputs'/'method1_programmatic.csv').exists(),
  'openai_api_key': bool(os.getenv('OPENAI_API_KEY')),
  'low_cost_model': os.getenv('LOW_COST_MODEL','gpt-6-luna'),
  'expensive_model': os.getenv('EXPENSIVE_MODEL','gpt-6.1-sol'),
}
print(json.dumps(checks,indent=2))
if checks['invoices'] != 50 or checks['ground_truth'] != 50:
    sys.exit('Expected 50 PDFs and 50 ground-truth files.')
