from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOLUME_MANIFEST_PATH = ROOT / "data" / "metadata" / "volume_manifest.json"
REVIEW_DIR = ROOT / "data" / "metadata" / "review"
REVIEW_MANIFEST_PATH = REVIEW_DIR / "review_manifest.json"


def build_review_manifest(source_manifest: dict) -> dict:
    entries = []
    for volume in source_manifest["volumes"]:
        entries.append(
            {
                "volume_id": volume["volume_id"],
                "title": volume["title"],
                "review_status": "pending",
                "review_scope": "sample",
                "issues_count": 0,
                "last_reviewed_at": None,
                "notes": "",
            }
        )

    return {"volumes": entries}


def main() -> None:
    if REVIEW_MANIFEST_PATH.exists():
        raise SystemExit(f"review manifest already exists: {REVIEW_MANIFEST_PATH}")

    source_manifest = json.loads(VOLUME_MANIFEST_PATH.read_text(encoding="utf-8"))
    review_manifest = build_review_manifest(source_manifest)

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_MANIFEST_PATH.write_text(
        json.dumps(review_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {REVIEW_MANIFEST_PATH}")


if __name__ == "__main__":
    main()
