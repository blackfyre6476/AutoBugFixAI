from fastapi import APIRouter, HTTPException

from models.fix_run import (
    ApplyApprovedFixRequest,
    ApplyApprovedFixResponse,
    AuditRequest,
    AuditResponse,
    FixRunRequest,
    FixRunResponse,
)
from orchestrator.engine import OrchestrationEngine
from repository import GitRepositoryManager
from repository.auditor import audit_repository

router = APIRouter(prefix="/api/v1/fixes", tags=["Fix runs"])


@router.post("/analyze", response_model=FixRunResponse, summary="Analyze a bug and validate a repair proposal")
async def analyze_bug(request: FixRunRequest) -> FixRunResponse:
    try:
        result = await OrchestrationEngine().run_pipeline(**request.model_dump())
        return FixRunResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/apply-approved", response_model=ApplyApprovedFixResponse, summary="Apply an explicitly approved candidate to a new Git branch")
async def apply_approved_fix(request: ApplyApprovedFixRequest) -> ApplyApprovedFixResponse:
    if not request.approval_confirmed:
        raise HTTPException(status_code=400, detail="approval_confirmed must be true before AutoFix writes to a repository")
    try:
        result = GitRepositoryManager().apply_approved_fix(request.repository_path, [operation.model_dump() for operation in request.candidate_operations], request.branch_name, request.commit_message)
        return ApplyApprovedFixResponse(status="applied_and_committed", **result, pull_request_summary=f"{request.commit_message}. AutoFix applied {len(request.candidate_operations)} reviewed edit(s), committed {result['commit_sha'][:8]}, and preserved the original branch.")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/audit", response_model=AuditResponse, summary="Scan a repository for bug patterns and return candidate fixes with exact file + line locations")
async def audit_repo(request: AuditRequest) -> AuditResponse:
    try:
        candidates = audit_repository(request.repository_path, request.bug_description)
        return AuditResponse(
            repository_path=request.repository_path,
            bug_description=request.bug_description,
            candidates=candidates,
            total_found=len(candidates),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

