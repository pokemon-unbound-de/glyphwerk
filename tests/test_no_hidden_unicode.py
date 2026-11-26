"""The repository must not contain invisible or direction-changing Unicode characters.

Such characters can hide code from reviewers ("Trojan Source") or hide instructions aimed at
AI review tools. See CONTRIBUTING.md, "Using AI tools", rule 6.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".py", ".md", ".json", ".toml", ".yml", ".yaml", ".txt", ".cfg", ".ini", ".lua", ".js", ".html"}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", "build", "dist"}

FORBIDDEN = {
    *range(0x200B, 0x2010),  # zero-width characters, LRM/RLM
    *range(0x202A, 0x202F),  # bidi embeddings and overrides
    *range(0x2060, 0x2065),  # word joiner, invisible operators
    *range(0x2066, 0x206A),  # bidi isolates
    0xFEFF,  # zero-width no-break space / BOM
    0x00AD,  # soft hyphen
    0x180E,
    0x115F, 0x1160, 0x3164, 0xFFA0,  # Hangul fillers
    *range(0xE0000, 0xE0080),  # Unicode tag characters
}


def _text_files():
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and not (SKIP_DIRS & set(path.relative_to(ROOT).parts)):
            yield path


def find_hidden(text: str) -> list[tuple[int, int]]:
    """Return (line, codepoint) for every forbidden character in ``text``."""
    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for ch in line:
            if ord(ch) in FORBIDDEN:
                hits.append((line_no, ord(ch)))
    return hits


def test_detector_finds_hidden_characters():
    assert find_hidden("plain text") == []
    assert find_hidden("a" + chr(0x200B) + "b") == [(1, 0x200B)]
    assert find_hidden("x\n" + chr(0x202E) + "evil") == [(2, 0x202E)]
    assert find_hidden("tag " + chr(0xE0041)) == [(1, 0xE0041)]


def test_repository_has_no_hidden_characters():
    problems = []
    for path in _text_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, cp in find_hidden(text):
            problems.append(f"{path.relative_to(ROOT)}:{line_no} U+{cp:04X}")
    assert not problems, "Invisible or bidi characters found:\n" + "\n".join(problems[:50])
