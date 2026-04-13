from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOLUME_DIR = ROOT / "data" / "raw" / "books" / "volumes"
MARKER_DIR = ROOT / "data" / "markdown" / "marker"
MARKITDOWN_DIR = ROOT / "data" / "markdown" / "markitdown"
LOG_DIR = ROOT / "data" / "staging" / "logs"


def run_command(command: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log_file:
        result = subprocess.run(command, stdout=log_file, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        raise SystemExit(f"command failed: {' '.join(command)}")


def convert_with_marker(volume_id: str) -> None:
    input_pdf = VOLUME_DIR / f"{volume_id}.pdf"
    output_dir = MARKER_DIR / volume_id
    log_path = LOG_DIR / f"{volume_id}.marker.log"
    output_dir.mkdir(parents=True, exist_ok=True)
    run_command([
        "marker_single",
        str(input_pdf),
        "--output_dir",
        str(output_dir),
        "--output_format",
        "markdown",
    ], log_path)


def convert_with_markitdown(volume_id: str) -> None:
    input_pdf = VOLUME_DIR / f"{volume_id}.pdf"
    output_path = MARKITDOWN_DIR / f"{volume_id}.md"
    log_path = LOG_DIR / f"{volume_id}.markitdown.log"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as output_file, log_path.open("w", encoding="utf-8") as log_file:
        result = subprocess.run(["markitdown", str(input_pdf)], stdout=output_file, stderr=log_file, text=True)
    if result.returncode != 0:
        raise SystemExit(f"markitdown failed for {volume_id}")


def flatten_marker_output(volume_id: str) -> None:
    output_dir = MARKER_DIR / volume_id
    candidate = next(output_dir.glob("*.md"), None)
    if candidate is None:
        raise SystemExit(f"no markdown output found in {output_dir}")
    final_path = MARKER_DIR / f"{volume_id}.md"
    shutil.copyfile(candidate, final_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("volume_id")
    parser.add_argument("--engine", choices=["marker", "markitdown"], default="marker")
    args = parser.parse_args()

    if args.engine == "marker":
        convert_with_marker(args.volume_id)
        flatten_marker_output(args.volume_id)
    else:
        convert_with_markitdown(args.volume_id)

    print(f"done {args.volume_id}")


if __name__ == "__main__":
    main()
