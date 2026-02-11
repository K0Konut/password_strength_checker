from checker import evaluate_password


def _get_check(result, name: str):
    for check in result.checks:
        if check.name == name:
            return check
    raise AssertionError(f"missing check: {name}")


def test_empty_password():
    result = evaluate_password("")
    assert result.score == 0
    assert result.label == "Faible"


def test_only_lowercase():
    result = evaluate_password("abcdefgh")
    assert result.label == "Faible"
    assert not _get_check(result, "sequence").passed


def test_lowercase_digits_sequence():
    result = evaluate_password("abcd1234")
    assert result.label == "Faible"
    assert not _get_check(result, "sequence").passed


def test_all_types_long():
    result = evaluate_password("Aa1!Aa1!Aa1!Aa1!")
    assert result.score >= 60
    assert result.label in ("Fort", "Très fort")


def test_repetition():
    result = evaluate_password("aaaaaaaaAA1!")
    assert not _get_check(result, "repetition").passed


def test_common_password():
    result = evaluate_password("password")
    assert not _get_check(result, "common").passed


def test_dictionary_word():
    result = evaluate_password("Sunshine2024!")
    assert not _get_check(result, "dictionary").passed
