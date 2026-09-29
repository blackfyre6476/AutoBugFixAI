from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from agents.workflow_agents import BugInvestigator, FixGenerator, RepositoryAnalyst
from sandbox.runner import IsolatedTestRunner


class OrchestrationEngine:
    async def run_pipeline(self, repository_path: str, bug_description: str, test_command: str = "pytest", candidate_operations: list | None = None) -> dict:
        repo = Path(repository_path).expanduser().resolve()
        if not repo.is_dir():
            raise ValueError("repository_path must point to an existing directory")
        context = {"repository_path": str(repo), "bug_description": bug_description}
        journey = []
        analyst = await RepositoryAnalyst().execute(context)
        context["analysis_files"] = analyst["files"]
        journey.append({"agent": "Repository Analyst", "status": "completed", "summary": analyst["summary"]})
        investigation = await BugInvestigator().execute(context)
        context.update(investigation)
        journey.append({"agent": "Bug Investigator", "status": "completed", "summary": investigation["root_cause"]})
        proposal = await FixGenerator().execute(context)
        operations = candidate_operations or proposal.get("candidate_operations", [])
        journey.append({"agent": "Fix Generator", "status": "completed", "summary": "Generated a review-only repair proposal."})
        runner = IsolatedTestRunner()
        validation = runner.run(str(repo), test_command, operations)
        journey.append({"agent": "Validation Agent", "status": "completed" if validation["passed"] else "failed", "summary": "Validation command completed in a disposable workspace."})
        regression = runner.run(str(repo), test_command, operations)
        journey.append({"agent": "Regression Agent", "status": "completed" if regression["passed"] else "failed", "summary": "Regression command completed in a fresh disposable workspace."})
        successful = bool(operations) and validation["passed"] and regression["passed"]
        return {
            "run_id": str(uuid4()), "status": "ready_for_review" if successful else "validation_failed", "journey": journey,
            "repository_summary": analyst["summary"], "affected_files": investigation["affected_files"],
            "root_cause": proposal["root_cause"], "proposed_fix": proposal["proposed_fix"], "patch_preview": proposal["patch_preview"],
            "candidate_operations": operations,
            "validation": validation, "regression": regression,
            "pull_request_summary": f"AutoFix proposal: {proposal['proposed_fix']} Candidate validation {'passed' if successful else 'needs attention'}; original repository was not modified.",
            "llm_mode": proposal["llm_mode"],
        }
