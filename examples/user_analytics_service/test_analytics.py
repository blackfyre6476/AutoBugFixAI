"""Tests for analytics.py — designed to fail with logical/assertion errors, not raw exceptions."""
import pytest
from analytics import calculate_conversion_rate, format_user_summary


# ── calculate_conversion_rate ─────────────────────────────────────────────────

def test_conversion_rate_normal():
    """50 conversions out of 200 visitors should be 25 %."""
    assert calculate_conversion_rate(50, 200) == 25.0


def test_conversion_rate_zero_visitors():
    """Zero visitors must return 0.0, not raise ZeroDivisionError.

    Bug location: analytics.py line 3 — missing zero-denominator guard.
    """
    try:
        result = calculate_conversion_rate(0, 0)
    except ZeroDivisionError:
        raise AssertionError(
            "calculate_conversion_rate(0, 0) raised ZeroDivisionError.\n"
            "  File: analytics.py  Line: 3\n"
            "  Fix : add 'if total_visitors == 0: return 0.0' before the division."
        ) from None
    assert result == 0.0, f"Expected 0.0 when total_visitors=0, got {result!r}."


def test_conversion_rate_zero_conversions():
    """Zero conversions with real visitors should be 0.0 %."""
    assert calculate_conversion_rate(0, 100) == 0.0


def test_conversion_rate_full():
    """100 % conversion rate should equal 100.0."""
    assert calculate_conversion_rate(500, 500) == 100.0


# ── format_user_summary ───────────────────────────────────────────────────────

def test_format_user_summary_normal():
    """A complete user dict should format correctly."""
    data = {"name": "Alice", "email": "alice@example.com"}
    assert format_user_summary(data) == "Alice <alice@example.com>"


def test_format_user_summary_missing_email():
    """A user without 'email' key must return a safe fallback, not raise KeyError.

    Bug location: analytics.py line 9 — direct dict['email'] access without .get().
    """
    data = {"name": "Bob"}
    try:
        result = format_user_summary(data)
    except KeyError as exc:
        raise AssertionError(
            f"format_user_summary({{'name': 'Bob'}}) raised KeyError({exc}).\n"
            "  File: analytics.py  Line: 9\n"
            "  Fix : replace  email = user_data['email']\n"
            "        with     email = user_data.get('email', '<no-email>')"
        ) from None
    assert isinstance(result, str), (
        f"Expected a string when email is absent, got {type(result).__name__!r}."
    )
    assert "<no-email>" in result or "Bob" in result, (
        "Return value should include the name or a clear fallback for the missing email."
    )


def test_format_user_summary_anonymous():
    """Missing name should fall back to 'Anonymous'."""
    data = {"email": "anon@example.com"}
    assert format_user_summary(data) == "Anonymous <anon@example.com>"

