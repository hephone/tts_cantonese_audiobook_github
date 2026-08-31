"""Regression tests for Cantonese TTS input safety."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "normalize_cantonese_tts.py"
)
SPEC = importlib.util.spec_from_file_location("normalizer", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
normalizer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(normalizer)


class TraditionalChineseValidationTests(unittest.TestCase):
    def test_rejects_convertible_simplified_chinese(self) -> None:
        with self.assertRaisesRegex(ValueError, "Traditional Chinese"):
            normalizer.validate_traditional_text("海龟", Path("sample.md"))

    def test_accepts_hong_kong_traditional_chinese(self) -> None:
        normalizer.validate_traditional_text(
            "海龜、一齊食曬佢；不請自來。",
            Path("sample.md"),
        )

    def test_rejects_equal_dictionary_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            dictionary = Path(temporary_directory) / "dictionary.tsv"
            dictionary.write_text("看\t看\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must differ"):
                normalizer.read_dictionary(dictionary)

    def test_bundled_dictionary_keeps_only_pronunciation_compatibility(self) -> None:
        entries = normalizer.read_dictionary(normalizer.DEFAULT_DICTIONARY)
        self.assertEqual(entries["噉"], "咁")
        self.assertNotIn("是", entries)
        self.assertNotIn("不是", entries)


if __name__ == "__main__":
    unittest.main()
