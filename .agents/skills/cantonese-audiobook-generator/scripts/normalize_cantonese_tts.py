#!/usr/bin/env python3
"""Create a TTS-only Cantonese script using deterministic replacements."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


DEFAULT_DICTIONARY = (
    Path(__file__).resolve().parent.parent
    / "references"
    / "cantonese-tts-pronunciations.tsv"
)


def read_dictionary(path: Path) -> dict[str, str]:
    """Read source/replacement pairs from a UTF-8 TSV file."""
    entries: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        columns = raw_line.split("\t")
        if len(columns) < 2:
            raise ValueError(f"{path}:{line_number}: expected tab-separated fields")

        source = columns[0].strip()
        replacement = columns[1].strip()
        if not source or not replacement:
            raise ValueError(f"{path}:{line_number}: source and replacement are required")
        if source == replacement:
            raise ValueError(f"{path}:{line_number}: source and replacement must differ")
        if source in entries and entries[source] != replacement:
            raise ValueError(f"{path}:{line_number}: conflicting replacement for {source!r}")
        entries[source] = replacement
    return entries


def normalize(text: str, replacements: dict[str, str]) -> tuple[str, Counter[str]]:
    """Apply replacements once, preferring longer source strings."""
    if not replacements:
        return text, Counter()

    sources = sorted(replacements, key=lambda value: (-len(value), value))
    pattern = re.compile("|".join(re.escape(source) for source in sources))
    counts: Counter[str] = Counter()

    def replace(match: re.Match[str]) -> str:
        source = match.group(0)
        counts[source] += 1
        return replacements[source]

    return pattern.sub(replace, text), counts


def normalize_tts_punctuation(text: str) -> tuple[str, int]:
    """Remove editorial slash pause marks before plain-text edge-tts synthesis.

    A slash may be useful to an editor reading a Cantonese script, but the
    edge-tts CLI speaks it aloud. URLs are first rewritten into a speakable
    label; every remaining slash becomes a light punctuation pause.
    """
    slash_count = text.count("/")
    if not slash_count:
        return text, 0

    prepared = re.sub(r"(?:網址：)?https?://", "網址：", text, flags=re.IGNORECASE)
    prepared = prepared.replace("/", "，")
    prepared = re.sub(r"，+([。！？；])", r"\1", prepared)
    prepared = re.sub(r"([。！？；])，+", r"\1", prepared)
    return prepared, slash_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an edge-tts-compatible copy without changing the reading script."
    )
    parser.add_argument("input", type=Path, help="Cantonese reading script")
    parser.add_argument("output", type=Path, help="TTS-only output text")
    parser.add_argument(
        "--book-dictionary",
        type=Path,
        help="Optional UTF-8 TSV whose entries override the bundled dictionary",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    if input_path == output_path:
        raise ValueError("input and output must differ; never overwrite the reading script")

    replacements = read_dictionary(DEFAULT_DICTIONARY)
    if args.book_dictionary is not None:
        replacements.update(read_dictionary(args.book_dictionary))

    source_text = input_path.read_text(encoding="utf-8")
    normalized_text, counts = normalize(source_text, replacements)
    normalized_text, slash_count = normalize_tts_punctuation(normalized_text)
    if "/" in normalized_text:
        raise ValueError("TTS text still contains '/', which edge-tts would read aloud")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_name(f".{output_path.name}.tmp")
    with temporary_path.open("w", encoding="utf-8", newline="\n") as output_file:
        output_file.write(normalized_text)
    temporary_path.replace(output_path)

    total = sum(counts.values())
    details = ", ".join(
        f"{source}→{replacements[source]}: {count}"
        for source, count in sorted(counts.items())
    )
    print(f"Created {output_path} with {total} replacement(s).")
    if details:
        print(details)
    if slash_count:
        print(f"/→punctuation: {slash_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
