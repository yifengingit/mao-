from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIRS = [
    ROOT / "data" / "markdown" / "marker",
    ROOT / "data" / "markdown" / "markitdown",
]
CLEAN_DIR = ROOT / "data" / "clean" / "volumes"


def should_merge_block(lines: list[str]) -> bool:
    if len(lines) < 2:
        return False

    first = lines[0].strip()
    if first == "注　　释":
        return False
    if re.match(r"^[　 ]*[*＊]", first):
        return False
    if re.match(r"^[　 ]*〔\d+〕", first):
        return False
    return True


def is_protected_heading_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if re.fullmatch(r"[（(][一二三四五六七八九十〇零○九\d年月日\s]+[）)]", stripped):
        return True
    if re.match(r"^第[一二三四五六七八九十]+[编章节部分件](?:[　\s]|$)", stripped):
        return True
    return False


def should_keep_block_split(lines: list[str]) -> bool:
    if len(lines) != 2:
        return False

    return is_protected_heading_line(lines[0])


def split_inline_protected_heading(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped:
        return []

    match = re.search(r"(?<=[。！？!”’）)])(第[一二三四五六七八九十]+[编章节部分件](?:[　\s]|$))", stripped)
    if not match:
        return [stripped]
    return [stripped[: match.start()], stripped[match.start() :]]


def merge_block_lines(lines: list[str]) -> list[str]:
    merged: list[str] = []
    current = ""

    for line in lines:
        stripped = line.strip()
        if is_protected_heading_line(stripped):
            if current:
                merged.append(current)
                current = ""
            merged.append(stripped)
            continue
        parts = split_inline_protected_heading(stripped)
        current += parts[0]
        if len(parts) == 2:
            if current:
                merged.append(current)
                current = ""
            merged.append(parts[1])

    if current:
        merged.append(current)
    return merged


def merge_hard_wrapped_blocks(lines: list[str]) -> list[str]:
    blocks: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        if line.strip():
            current.append(line)
            continue
        if current:
            blocks.append(current)
            current = []
        blocks.append([line])

    if current:
        blocks.append(current)

    merged: list[str] = []
    for block in blocks:
        if len(block) == 1 and not block[0].strip():
            merged.append(block[0])
        elif should_keep_block_split(block):
            merged.extend(block)
        elif should_merge_block(block):
            merged.extend(merge_block_lines(block))
        else:
            merged.extend(block)
    return merged


def should_merge_short_fragment(previous: str, following: str) -> bool:
    if len(previous) > 8:
        return False
    if not re.search(r"[A-Za-z\u4e00-\u9fff]$", previous):
        return False
    if not re.match(r"^[A-Za-z\u4e00-\u9fff]", following):
        return False
    if len(following) < 6:
        return bool(re.search(r"[。！？]$", following) and len(following) >= 2)
    return True


def should_merge_across_blank_line(previous_line: str, next_line: str) -> bool:
    previous = previous_line.strip()
    following = next_line.strip()

    if not previous or not following:
        return False
    if re.match(r"^[　 ]*(注　　释|[*＊]|〔\d+〕)", previous):
        return False
    if re.match(r"^[　 ]*(注　　释|[*＊]|〔\d+〕)", following):
        return False
    if is_protected_heading_line(previous) or is_protected_heading_line(following):
        return False
    if re.search(r"[。！？：；]$", previous):
        return False
    if re.match(r"^[一二三四五六七八九十]+[、，.]", following):
        return False
    if re.search(r"[A-Za-z\u4e00-\u9fff]$", previous) and re.match(r"^[A-Za-z\u4e00-\u9fff]", following):
        if re.search(r"[。！？]$", following) and len(following) <= 4:
            return True
        if re.search(r"[，、；：。！？]", following) and len(following) <= 10:
            return True
    if len(previous) >= 12 and len(following) >= 12:
        return True
    return should_merge_short_fragment(previous, following)


def merge_spurious_blank_lines(lines: list[str]) -> list[str]:
    merged: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        previous_nonblank = merged[-1] if merged and merged[-1].strip() else ""

        # Try three blank lines first
        if (
            line.strip()
            and index + 4 < len(lines)
            and not lines[index + 1].strip()
            and not lines[index + 2].strip()
            and not lines[index + 3].strip()
            and previous_nonblank != "注　　释"
            and not re.match(r"^[　 ]*〔\d+〕", previous_nonblank.strip())
            and should_merge_across_blank_line(line, lines[index + 4])
        ):
            merged.append(line + lines[index + 4].strip())
            index += 5
            continue

        # Try two blank lines
        if (
            line.strip()
            and index + 3 < len(lines)
            and not lines[index + 1].strip()
            and not lines[index + 2].strip()
            and previous_nonblank != "注　　释"
            and not re.match(r"^[　 ]*〔\d+〕", previous_nonblank.strip())
            and should_merge_across_blank_line(line, lines[index + 3])
        ):
            merged.append(line + lines[index + 3].strip())
            index += 4
            continue

        # Try one blank line
        if (
            line.strip()
            and index + 2 < len(lines)
            and not lines[index + 1].strip()
            and previous_nonblank != "注　　释"
            and not re.match(r"^[　 ]*〔\d+〕", previous_nonblank.strip())
            and should_merge_across_blank_line(line, lines[index + 2])
        ):
            merged.append(line + lines[index + 2].strip())
            index += 3
            continue

        merged.append(line)
        index += 1

    return merged


def clean_text(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    filtered: list[str] = []

    for line in lines:
        if re.fullmatch(r"\d+", line.strip()):
            continue
        filtered.append(line)

    filtered = merge_hard_wrapped_blocks(filtered)
    filtered = merge_spurious_blank_lines(filtered)
    text = "\n".join(filtered)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def find_input_path(volume_id: str) -> Path:
    for raw_dir in RAW_DIRS:
        candidate = raw_dir / f"{volume_id}.md"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No raw markdown found for {volume_id} in marker/ or markitdown/")


def read_text_with_fallback(path: Path) -> str:
    encodings = ["utf-8", "utf-8-sig", "gbk", "cp936"]
    last_error: UnicodeDecodeError | None = None
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Unable to read file: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("volume_id")
    args = parser.parse_args()

    input_path = find_input_path(args.volume_id)
    output_path = CLEAN_DIR / f"{args.volume_id}.cleaned.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    text = read_text_with_fallback(input_path)
    cleaned = clean_text(text)
    output_path.write_text(cleaned, encoding="utf-8")
    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
