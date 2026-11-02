from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for folder,extension in [('invoices','pdf'),('ground_truth','json')]:
 paths=list((ROOT/folder).glob('*.'+extension))
 if len(paths)!=50:raise SystemExit(f'Expected 50 {folder} files, found {len(paths)}. Run scripts/setup_data.py first.')
print('Input files ready. The default local LLM path requires a free CUDA GPU, not an API key.')
