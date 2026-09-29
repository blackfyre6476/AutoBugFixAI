import pytest
from analytics import calculate_conversion_rate


def test_conversion_rate_zero_visitors():
    """Triggers ZeroDivisionError in analytics.py at line 3 when denominator is zero."""
    assert calculate_conversion_rate(10, 0) == 0.0
