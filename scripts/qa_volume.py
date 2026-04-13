from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "data" / "clean" / "volumes"
QA_DIR = ROOT / "data" / "metadata" / "qa"


def build_report(text: str, volume_id: str) -> dict:
    lines = text.splitlines()
    return {
        "volume_id": volume_id,
        "line_count": len(lines),
        "heading_count": sum(1 for line in lines if line.startswith("#")),
        "blank_line_count": sum(1 for line in lines if not line.strip()),
        "digit_only_line_count": sum(1 for line in lines if re.fullmatch(r"\d+", line.strip() or "")),
        "needs_manual_review": True,
        "manual_review_checks": [
            "标题完整性",
            "段落连贯性",
            "页码回溯",
            "OCR 错字",
            "脚注/多栏/表格异常"
        ]
    }


def main(volume_id: str) -> None:
    input_path = CLEAN_DIR / f"{volume_id}.cleaned.md"
    output_path = QA_DIR / f"{volume_id}.qa.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    text = input_path.read_text(encoding="utf-8")
    report = build_report(text, volume_id)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {output_path}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
