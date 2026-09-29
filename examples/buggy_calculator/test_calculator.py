from calculator import divide


def test_zero_denominator_returns_safe_fallback():
    assert divide(12, 0) == 0
