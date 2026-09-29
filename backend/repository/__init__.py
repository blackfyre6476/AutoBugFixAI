"""Safe Git operations for explicitly approved AutoFix changes."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


from repository.patcher import apply_patch_operations


class GitRepositoryManager:
    def _git(self, repo: Path, *args: str) -> str:
        result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise ValueError((result.stderr or result.stdout).strip() or "Git command failed")
        return result.stdout.strip()

    def apply_approved_fix(self, repository_path: str, operations: list[dict[str, Any]], branch_name: str, commit_message: str) -> dict[str, str]:
        repo = Path(repository_path).expanduser().resolve()
        if not repo.is_dir():
            raise ValueError("repository_path must point to an existing directory")
        self._git(repo, "rev-parse", "--is-inside-work-tree")
        if self._git(repo, "status", "--porcelain"):
            raise ValueError("Repository has uncommitted changes. Commit or stash them before applying an approved fix.")
        if self._git(repo, "branch", "--list", branch_name):
            raise ValueError(f"Branch already exists: {branch_name}")
        self._git(repo, "checkout", "-b", branch_name)
        try:
            success, message = apply_patch_operations(repo, operations)
            if not success:
                raise ValueError(message)
            diff = self._git(repo, "diff", "--", ".")
            if not diff:
                raise ValueError("The approved operations produced no changes.")
            self._git(repo, "add", "--", ".")
            self._git(repo, "commit", "-m", commit_message)
            return {"branch_name": branch_name, "commit_sha": self._git(repo, "rev-parse", "HEAD"), "diff": diff}
        except Exception:
            self._git(repo, "checkout", "-")
            self._git(repo, "branch", "-D", branch_name)
            raise
