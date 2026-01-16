from password_strength_checker.core.evaluate import evaluate


def test_estimates_present():
    r = evaluate("password")
    assert len(r.estimates) == 4


def test_dictionary_reduces_estimates():
    r = evaluate("password")
    # offline fast hash GPU (index 2)
    secs = float(r.estimates[2]["seconds"])
    assert secs < 60  # doit être crackable rapidement


def test_strong_has_longer_estimates_than_weak():
    weak = evaluate("password")
    strong = evaluate("mV7!pQ2#zL9@tX__2026!")  # long + diverse

    weak_secs = float(weak.estimates[2]["seconds"])     # offline fast hash GPU
    strong_secs = float(strong.estimates[2]["seconds"]) # offline fast hash GPU

    assert strong_secs > weak_secs
