"""Download UCI's unmodified Excel workbook; keep it out of version control."""
from pathlib import Path
import hashlib
import json
import urllib.request
import zipfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
DEST = ROOT / "data" / "raw" / "Online Retail.xlsx"


def download() -> Path:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        archive = Path(temp) / "download.zip"
        urllib.request.urlretrieve(URL, archive)
        with zipfile.ZipFile(archive) as z:
            choices = [name for name in z.namelist() if name.lower().endswith(".xlsx")]
            if len(choices) != 1:
                raise RuntimeError(f"Expected one workbook in UCI archive; got {choices}")
            with z.open(choices[0]) as source, DEST.open("wb") as target:
                import shutil
                shutil.copyfileobj(source, target)
    with DEST.open("rb") as downloaded_file:
        digest = hashlib.file_digest(downloaded_file, "sha256").hexdigest()
    info = {"download_url": URL, "file": str(DEST.relative_to(ROOT)),
            "sha256": digest, "bytes": DEST.stat().st_size, "license": "CC BY 4.0",
            "retrieved_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}
    (ROOT / "data/raw/source_manifest.json").write_text(json.dumps(info, indent=2))
    return DEST


if __name__ == "__main__":
    try:
        print(f"Downloaded original workbook: {download()}")
    except Exception as error:
        raise SystemExit(f"Could not download from UCI: {error}\nDownload manually from https://archive.ics.uci.edu/dataset/352/online+retail and place 'Online Retail.xlsx' in data/raw/.")
