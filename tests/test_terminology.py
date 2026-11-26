from glyphwerk.gates.terminology import TermFinding, check_terminology


def test_reports_every_occurrence_with_start_position():
    text = "Pokeball and another Pokeball"
    findings = check_terminology(
        text,
        [{"blocked": "Pokeball", "preferred": "Poké Ball"}],
    )

    assert [finding.start for finding in findings] == [0, text.rindex("Pokeball")]
    assert [finding.blocked for finding in findings] == ["Pokeball", "Pokeball"]
    assert all(finding.preferred == "Poké Ball" for finding in findings)
    assert all("Pokeball" in finding.context for finding in findings)


def test_case_sensitive_rule_only_matches_exact_case():
    text = "Pokeball and pokeball"

    assert len(check_terminology(text, [{"blocked": "Pokeball"}])) == 2
    assert len(check_terminology(text, [{"blocked": "Pokeball", "case_sensitive": True}])) == 1


def test_word_boundary_does_not_match_larger_word():
    assert check_terminology("Pokeballs", [{"blocked": "Pokeball"}]) == []


def test_term_finding_keeps_compatible_default_start():
    finding = TermFinding("Pokeball", "Poké Ball", "Pokeball")
    assert finding.start == 0
