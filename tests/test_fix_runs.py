from pathlib import Path
import subprocess
from fastapi.testclient import TestClient


def test_rejects_unsafe_test_command(test_client: TestClient, tmp_path: Path):
    response = test_client.post("/api/v1/fixes/analyze", json={"repository_path": str(tmp_path), "bug_description": "A sufficiently descriptive sample bug", "test_command": "pytest; whoami"})
    assert response.status_code == 422


def test_runs_safe_workflow(test_client: TestClient, tmp_path: Path):
    (tmp_path / "calculator.py").write_text("def divide(a, b):\n    return a / b\n", encoding="utf-8")
    (tmp_path / "test_sample.py").write_text("from calculator import divide\n\ndef test_zero_is_safe():\n    assert divide(2, 0) == 0\n", encoding="utf-8")
    response = test_client.post("/api/v1/fixes/analyze", json={"repository_path": str(tmp_path), "bug_description": "ZeroDivisionError: division by zero in calculator", "test_command": "pytest", "candidate_operations": [{"file_path": "calculator.py", "search": "    return a / b", "replacement": "    if b == 0:\n        return 0\n    return a / b"}]})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready_for_review"
    assert data["llm_mode"] == "heuristic_fallback"
    assert len(data["journey"]) == 5
    assert data["validation"]["passed"] is True
    assert data["validation"]["patch_applied"] is True
    assert "zero denominator" in data["proposed_fix"].lower()
    assert (tmp_path / "calculator.py").read_text(encoding="utf-8") == "def divide(a, b):\n    return a / b\n"


def test_rejects_patch_path_outside_repository(test_client: TestClient, tmp_path: Path):
    response = test_client.post("/api/v1/fixes/analyze", json={"repository_path": str(tmp_path), "bug_description": "A sufficiently descriptive sample bug", "candidate_operations": [{"file_path": "../outside.py", "search": "x", "replacement": "y"}]})
    assert response.status_code == 422


def test_applies_explicitly_approved_fix_on_autofix_branch(test_client: TestClient, tmp_path: Path):
    (tmp_path / "service.py").write_text("enabled = False\n", encoding="utf-8")
    for args in (("init",), ("config", "user.email", "test@example.com"), ("config", "user.name", "Test User"), ("add", "."), ("commit", "-m", "initial")):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True, text=True)
    response = test_client.post("/api/v1/fixes/apply-approved", json={"repository_path": str(tmp_path), "approval_confirmed": True, "branch_name": "autofix/enable-service", "commit_message": "fix: enable service", "candidate_operations": [{"file_path": "service.py", "search": "enabled = False", "replacement": "enabled = True"}]})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "applied_and_committed"
    assert data["branch_name"] == "autofix/enable-service"
    assert "enabled = True" in data["diff"]
    assert (tmp_path / "service.py").read_text(encoding="utf-8") == "enabled = True\n"


def test_runs_safe_workflow_with_line_number(test_client: TestClient, tmp_path: Path):
    (tmp_path / "calculator.py").write_text("def divide(a, b):\n    return a / b\n", encoding="utf-8")
    (tmp_path / "test_sample.py").write_text("from calculator import divide\n\ndef test_zero_is_safe():\n    assert divide(2, 0) == 0\n", encoding="utf-8")
    response = test_client.post("/api/v1/fixes/analyze", json={"repository_path": str(tmp_path), "bug_description": "ZeroDivisionError: division by zero in calculator", "test_command": "pytest", "candidate_operations": [{"file_path": "calculator.py", "line_number": 2, "search": "    return a / b", "replacement": "    if b == 0:\n        return 0\n    return a / b"}]})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready_for_review"
    assert data["validation"]["passed"] is True
    assert data["candidate_operations"][0]["line_number"] == 2


def test_runs_line_number_direct_replacement(test_client: TestClient, tmp_path: Path):
    (tmp_path / "calculator.py").write_text("def divide(a, b):\n    return a / b\n", encoding="utf-8")
    (tmp_path / "test_sample.py").write_text("from calculator import divide\n\ndef test_zero_is_safe():\n    assert divide(2, 0) == 0\n", encoding="utf-8")
    response = test_client.post("/api/v1/fixes/analyze", json={"repository_path": str(tmp_path), "bug_description": "ZeroDivisionError: division by zero in calculator", "test_command": "pytest", "candidate_operations": [{"file_path": "calculator.py", "line_number": 2, "replacement": "    if b == 0:\n        return 0\n    return a / b"}]})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready_for_review"
    assert data["validation"]["passed"] is True

