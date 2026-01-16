from password_strength_checker.core.evaluate import evaluate


def test_very_weak_123456():
    r = evaluate("123456")
    assert r.score <= 30
    assert r.label in {"Very Weak", "Weak"}


def test_strong_randomish():
    r = evaluate("mV7!pQ2#zL9@tX")
    assert r.score >= 70


def test_dictionary_password():
    r = evaluate("password")
    assert r.score <= 30
    assert any(f.code.startswith("DICT") for f in r.findings)
