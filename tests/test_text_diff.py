"""Unit tests for glyphwerk.gates.text_diff."""
from glyphwerk.codec.pcs import encode
from glyphwerk.gates.text_diff import check_text_entry


def test_clean_pair_returns_no_findings():
    assert check_text_entry("Hello [player]!", "Hallo [player]!") == []


def test_buffer_mismatch_flagged():
    findings = check_text_entry("Hello [player]!", "Hallo Welt!")
    assert [f.code for f in findings] == ["BUFFER_MISMATCH"]


def test_glued_buffer_flagged_and_allowed_suffix_ignored():
    flagged = check_text_entry("[player] is here.", "[player]ist da.")
    assert [f.code for f in flagged] == ["GLUED_BUFFER"]

    allowed_single = check_text_entry("[player]'s bag", "[player]s Tasche")
    assert allowed_single == []

    allowed_unit = check_text_entry("[buffer1] cm", "[buffer1]cm")
    assert allowed_unit == []


def test_double_scroll_typo_flagged():
    findings = check_text_entry("This is fine.", "Das\\llist gut.")
    assert [f.code for f in findings] == ["DOUBLE_SCROLL_TYPO"]


def test_double_scroll_suspect_flagged_and_valid_l_word_allowed():
    suspect = check_text_entry("Check this.", "Prüfe\\llxyz jetzt.")
    assert [f.code for f in suspect] == ["DOUBLE_SCROLL_SUSPECT"]

    valid_l_word = check_text_entry("Dear friend", "Mein\\llieber Freund")
    assert valid_l_word == []


def test_unencodable_pcs_flagged():
    _, bad = encode("Preis: 10€")
    assert "€" in bad

    findings = check_text_entry("Price: 10", "Preis: 10€")
    assert [f.code for f in findings] == ["UNENCODABLE_PCS"]
