"""The repository must not contain invisible or direction-changing Unicode characters.

Such characters can hide code from reviewers ("Trojan Source") or hide instructions aimed at
AI review tools. See CONTRIBUTING.md, "Using AI tools", rule 6.
"""
from __future__ import annotations

import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".py", ".md", ".json", ".toml", ".yml", ".yaml", ".txt", ".cfg", ".ini", ".lua", ".js", ".html", ""}
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", "build", "dist"}

# Every character in Unicode category Cf (format characters: zero-width, bidi marks incl. U+061C ALM,
# embeddings, overrides, isolates, BOM, soft hyphen, tag characters, ...) is forbidden. In addition:
FORBIDDEN_EXTRA = {
    0x2028, 0x2029, 0x0085,  # line/paragraph separator, next line: editors show a line break, Python does not
    0x115F, 0x1160, 0x3164, 0xFFA0,  # Hangul fillers (category Lo, but render as nothing)
    *range(0xFE00, 0xFE0F),  # variation selectors 1-15
    *range(0xE0100, 0xE01F0),  # variation selectors supplement
}
EMOJI_VS = 0xFE0F  # allowed only directly after a symbol (emoji presentation)


def forbidden(ch: str, prev: str | None) -> bool:
    cp = ord(ch)
    if cp == EMOJI_VS:
        return prev is None or unicodedata.category(prev) not in ("So", "Sk", "Sm")
    return cp in FORBIDDEN_EXTRA or unicodedata.category(ch) == "Cf"


def _text_files():
    try:
        out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
        paths = [ROOT / p for p in out.decode("utf-8").split("\0") if p]
    except (OSError, subprocess.CalledProcessError):  # no git (e.g. sdist): fall back to the file tree
        paths = [p for p in ROOT.rglob("*") if not (SKIP_DIRS & set(p.relative_to(ROOT).parts))]
    for path in paths:
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def find_hidden(text: str) -> list[tuple[int, int]]:
    """Return (line, codepoint) for every forbidden character in ``text``.

    Lines are split on ``"\\n"`` only, so U+2028/U+2029/U+0085 are inspected instead of being taken as line breaks.
    """
    hits = []
    for line_no, line in enumerate(text.split("\n"), start=1):
        prev = None
        for ch in line:
            if forbidden(ch, prev):
                hits.append((line_no, ord(ch)))
            prev = ch
    return hits


def describe(line_no: int, cp: int) -> str:
    if cp == 0xFEFF and line_no == 1:
        return "U+FEFF at the start of the file: save it as UTF-8 without BOM"
    return f"U+{cp:04X} {unicodedata.name(chr(cp), 'unnamed')}"


def test_detector_finds_hidden_characters():
    assert find_hidden("plain text") == []
    assert find_hidden("a" + chr(0x200B) + "b") == [(1, 0x200B)]
    assert find_hidden("x\n" + chr(0x202E) + "evil") == [(2, 0x202E)]
    assert find_hidden("tag " + chr(0xE0041)) == [(1, 0xE0041)]
    assert find_hidden("alm" + chr(0x061C)) == [(1, 0x061C)]
    assert find_hidden("code" + chr(0x2028) + "comment") == [(1, 0x2028)]
    assert find_hidden("x\ny" + chr(0x0085)) == [(2, 0x0085)]
    assert find_hidden("text" + chr(0xFE01)) == [(1, 0xFE01)]
    assert find_hidden("text" + chr(0xE0100)) == [(1, 0xE0100)]
    assert find_hidden("A" + chr(0xFE0F)) == [(1, 0xFE0F)]


def test_emoji_presentation_selector_is_allowed():
    assert find_hidden(chr(0x2764) + chr(0xFE0F) + " heart") == []
    assert find_hidden("de " + chr(0x1F1E9) + chr(0x1F1EA)) == []


def test_bom_message_is_readable():
    assert "without BOM" in describe(1, 0xFEFF)
    assert describe(3, 0x200B).startswith("U+200B ZERO WIDTH SPACE")


def test_files_without_suffix_are_checked():
    names = {p.relative_to(ROOT).as_posix() for p in _text_files()}
    assert "LICENSE" in names


def test_repository_has_no_hidden_characters():
    problems = []
    for path in _text_files():
        data = path.read_bytes()
        if b"\0" in data:  # binary file
            continue
        text = data.decode("utf-8", errors="replace")
        for line_no, cp in find_hidden(text):
            problems.append(f"{path.relative_to(ROOT)}:{line_no} {describe(line_no, cp)}")
    assert not problems, "Invisible or bidi characters found:\n" + "\n".join(problems[:50])
