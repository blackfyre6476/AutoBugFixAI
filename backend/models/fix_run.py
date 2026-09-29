from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, field_validator


class FixRunRequest(BaseModel):
    repository_path: str = Field(min_length=1, description="Absolute path to a local source repository")
    bug_description: str = Field(min_length=10, max_length=12_000)
    test_command: str = Field(default="pytest", max_length=300)
    candidate_operations: list["PatchOperation"] = Field(default_factory=list, description="Optional review-approved edits to validate in the disposable copy")

    @field_validator("test_command")
    @classmethod
    def allow_safe_test_commands(cls, command: str) -> str:
        command = command.strip()
        allowed = ("pytest", "python -m pytest", "python -m unittest")
        if not command.startswith(allowed):
            raise ValueError("test_command must start with pytest, python -m pytest, or python -m unittest")
        if any(token in command for token in (";", "&&", "||", "|", ">", "<", "`")):
            raise ValueError("test_command contains an unsafe shell operator")
        return command


class JourneyStep(BaseModel):
    agent: str
    status: Literal["completed", "skipped", "failed"]
    summary: str


class PatchOperation(BaseModel):
    file_path: str = Field(min_length=1, max_length=500)
    line_number: int | None = Field(default=None, ge=1, description="Optional 1-indexed target line number for changes in code")
    search: str = Field(default="", max_length=10_000, description="Search text block to replace; optional if line_number is specified")
    replacement: str = Field(default="", max_length=10_000, description="Replacement content")

    @field_validator("file_path")
    @classmethod
    def require_relative_source_path(cls, file_path: str) -> str:
        if file_path.startswith(("/", "\\")) or ".." in file_path.replace("\\", "/").split("/"):
            raise ValueError("file_path must stay within the repository")
        return file_path.replace("\\", "/")


class TestEvidence(BaseModel):
    command: str
    passed: bool
    return_code: int
    output: str
    isolation: str
    patch_applied: bool = False
    patch_message: str = "No candidate patch was applied."


class FixRunResponse(BaseModel):
    run_id: str
    status: Literal["ready_for_review", "validation_failed", "failed"]
    journey: list[JourneyStep]
    repository_summary: str
    affected_files: list[str]
    root_cause: str
    proposed_fix: str
    patch_preview: str
    candidate_operations: list[PatchOperation]
    validation: TestEvidence
    regression: TestEvidence
    pull_request_summary: str
    llm_mode: Literal["openai_compatible", "heuristic_fallback"]


class ApplyApprovedFixRequest(BaseModel):
    repository_path: str = Field(min_length=1)
    candidate_operations: list[PatchOperation] = Field(min_length=1)
    approval_confirmed: bool = Field(description="Must be true to perform a repository write")
    branch_name: str = Field(default="autofix/approved-fix", min_length=8, max_length=80)
    commit_message: str = Field(default="fix: apply approved AutoFix candidate", min_length=10, max_length=180)

    @field_validator("branch_name")
    @classmethod
    def require_autofix_branch(cls, branch_name: str) -> str:
        if not branch_name.startswith("autofix/") or any(token in branch_name for token in ("..", " ", "~", "^", ":", "?", "*", "[", "\\")):
            raise ValueError("branch_name must be a safe branch name beginning with autofix/")
        return branch_name


class ApplyApprovedFixResponse(BaseModel):
    status: Literal["applied_and_committed"]
    branch_name: str
    commit_sha: str
    diff: str
    pull_request_summary: str


# ── Repository audit models ───────────────────────────────────────────────────

class AuditRequest(BaseModel):
    repository_path: str = Field(min_length=1, description="Absolute path to a local source repository")
    bug_description: str = Field(min_length=10, max_length=12_000, description="Bug description or error log used to select audit patterns")


class AuditCandidate(BaseModel):
    file_path: str
    line_number: int
    search: str
    replacement: str
    description: str = ""


class AuditResponse(BaseModel):
    repository_path: str
    bug_description: str
    candidates: list[AuditCandidate]
    total_found: int

