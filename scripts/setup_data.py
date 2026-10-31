from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def pick_archive(prefix: str) -> Path:
    exact = DATA / f"{prefix}.zip"
    if exact.exists():
        return exact
    matches = sorted(DATA.glob(f"{prefix}*.zip"))
    if not matches:
        raise FileNotFoundError(f"No {prefix}.zip archive found in {DATA}")
    return matches[0]

for prefix, target_name in [("pdf", "invoices"), ("ground_truth", "ground_truth")]:
    archive = pick_archive(prefix)
    target = ROOT / target_name
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(target)

    nested = [p for p in target.iterdir() if p.is_dir()]
    if len(nested) == 1 and not list(target.glob("*.pdf")) and not list(target.glob("*.json")):
        for p in nested[0].iterdir():
            p.replace(target / p.name)
        nested[0].rmdir()

    print(f"{archive.name} -> {target_name}/")
