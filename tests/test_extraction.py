from claim_extractor.extraction.base import normalise_whitespace

def test_collapses_runs_of_whitespace():
    result = normalise_whitespace("  Claimant   Name:\n\n  John    Smith  ")
    assert result == "Claimant Name: John Smith"

def test_collapses_runs_of_whitespace():
    assert normalise_whitespace("  a   b  ") == "a b"