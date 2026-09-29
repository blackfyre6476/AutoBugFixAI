# User Analytics Service - Test Repository

This test repository is designed for testing and demonstrating **AutoFix AI**.

## 🐛 Scenario 1: ZeroDivisionError Bug

- **File**: `analytics.py`
- **Bug Description**: `ZeroDivisionError: division by zero in calculate_conversion_rate when total_visitors is 0`
- **Test Command**: `pytest`
- **Candidate Operation**:
  - `search`: `return (conversions / total_visitors) * 100.0`
  - `replacement`:
```python
    if total_visitors == 0:
        return 0.0
    return (conversions / total_visitors) * 100.0
```

## 🐛 Scenario 2: KeyError Missing Email Bug

- **File**: `analytics.py`
- **Bug Description**: `KeyError: 'email' in format_user_summary when user_data dictionary lacks an email key`
- **Test Command**: `pytest`
- **Candidate Operation**:
  - `search`: `email = user_data["email"]`
  - `replacement`: `email = user_data.get("email", "no-email")`

## 🚀 How to Test with AutoFix AI API

### Analyze API Request Example (Scenario 1):
```json
POST http://localhost:8000/api/v1/fixes/analyze
{
  "repository_path": "C:\\Users\\saatv\\Videos\\examples\\user_analytics_service",
  "bug_description": "ZeroDivisionError: division by zero in calculate_conversion_rate when total_visitors is 0",
  "test_command": "pytest",
  "candidate_operations": [
    {
      "file_path": "analytics.py",
      "search": "    return (conversions / total_visitors) * 100.0",
      "replacement": "    if total_visitors == 0:\n        return 0.0\n    return (conversions / total_visitors) * 100.0"
    }
  ]
}
```
