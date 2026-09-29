def calculate_conversion_rate(conversions: int, total_visitors: int) -> float:
    """Calculate conversion rate percentage."""
    return (conversions / total_visitors) * 100.0


def format_user_summary(user_data: dict) -> str:
    """Format user summary string."""
    name = user_data.get("name", "Anonymous")
    email = user_data["email"]
    return f"{name} <{email}>"
