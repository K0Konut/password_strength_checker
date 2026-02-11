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


def test_keyboard_sequence():
    result = evaluate_password("qwerty12!")
    assert not _get_check(result, "keyboard").passed


def test_repeated_segment():
    result = evaluate_password("abcabc12!")
    assert not _get_check(result, "pattern").passed


def test_min_length_override():
    result = evaluate_password("Aa1!Aa1!Aa1!", min_length=16)
    assert "16" in _get_check(result, "length").message
    assert any("16" in suggestion for suggestion in result.suggestions)


def test_no_dictionary_check():
    result = evaluate_password("Sunshine2024!", use_dictionary=False)
    assert all(check.name != "dictionary" for check in result.checks)


def test_profile_lenient_min_length():
    result = evaluate_password("Aa1!Aa1!Aa1!", profile="lenient")
    assert "10" in _get_check(result, "length").message


def test_profile_strict_min_length():
    result = evaluate_password("Aa1!Aa1!Aa1!", profile="strict")
    assert "16" in _get_check(result, "length").message
