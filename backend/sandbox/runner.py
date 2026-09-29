from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import sys
from pathlib import Path
from typing import Any


from repository.patcher import apply_patch_operations


class IsolatedTestRunner:
    """Runs an allow-listed test command in a disposable copied workspace."""

    def run(self, repository_path: str, command: str, operations: list[dict[str, Any]] | None = None) -> dict:
        with tempfile.TemporaryDirectory(prefix="autofix-sandbox-") as temp_dir:
            target = Path(temp_dir) / "repository"
            try:
                shutil.copytree(repository_path, target, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv", "node_modules", ".pytest_cache", ".mypy_cache", ".ruff_cache"))
            except OSError as exc:
                return {"command": command, "passed": False, "return_code": 1, "output": f"Unable to prepare disposable workspace: {exc}", "isolation": "disposable local workspace", "patch_applied": False, "patch_message": "Candidate patch was not applied because the workspace copy failed."}
            patch_applied, patch_message = apply_patch_operations(target, operations or [])
            if operations and not patch_applied:
                return {"command": command, "passed": False, "return_code": 2, "output": "Candidate patch was not executed.", "isolation": "disposable local workspace", "patch_applied": False, "patch_message": patch_message}
            env = os.environ.copy()
            env.update({"PYTHONDONTWRITEBYTECODE": "1", "NO_PROXY": "*"})
            env.pop("HTTP_PROXY", None)
            env.pop("HTTPS_PROXY", None)
            try:
                args = [sys.executable, "-m", "pytest"] if command == "pytest" else command.split()
                result = subprocess.run(args, cwd=target, env=env, capture_output=True, text=True, timeout=60)
                output = (result.stdout + "\n" + result.stderr).strip()[-6000:]
                return {"command": command, "passed": result.returncode == 0, "return_code": result.returncode, "output": output, "isolation": "disposable local workspace", "patch_applied": patch_applied, "patch_message": patch_message}
            except subprocess.TimeoutExpired:
                return {"command": command, "passed": False, "return_code": 124, "output": "Test command timed out after 60 seconds.", "isolation": "disposable local workspace", "patch_applied": patch_applied, "patch_message": patch_message}
