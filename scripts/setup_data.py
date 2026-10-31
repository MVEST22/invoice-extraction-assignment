from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

for archive_name, target_name in [('pdf.zip', 'invoices'), ('ground_truth.zip', 'ground_truth')]:
    archive = DATA / archive_name
    target = ROOT / target_name
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(target)
    nested = [p for p in target.iterdir() if p.is_dir()]
    if len(nested) == 1 and not list(target.glob('*.pdf')) and not list(target.glob('*.json')):
        for p in nested[0].iterdir():
            p.replace(target / p.name)
        nested[0].rmdir()
    print(f'{archive_name} -> {target_name}/')
