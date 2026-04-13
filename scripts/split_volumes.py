from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfWriter

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "metadata" / "volume_manifest.json"
OUTPUT_DIR = ROOT / "data" / "raw" / "books" / "volumes"


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def split_volume(source_pdf: Path, volume: dict) -> Path:
    output_path = OUTPUT_DIR / f"{volume['volume_id']}.pdf"
    writer = PdfWriter()
    writer.append(str(source_pdf), pages=(volume["start_page"], volume["end_page"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        writer.write(f)
    return output_path


def main() -> None:
    manifest = load_manifest()
    source_pdf = ROOT / manifest["source_pdf"]
    for volume in manifest["volumes"]:
        if volume["end_page"] <= volume["start_page"]:
            print(f"skip {volume['volume_id']}: invalid page range")
            continue
        output_path = split_volume(source_pdf, volume)
        print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
