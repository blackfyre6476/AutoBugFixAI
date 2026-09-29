# AutoFix AI Working Plan

## Objective

Deliver a safe prototype that accepts a local source repository and a bug report, diagnoses the likely cause, proposes a repair, validates it in a disposable workspace, runs regression tests, and returns an approval-ready change summary.

## Scope

The prototype supports Python repositories and pytest commands. It keeps the original repository read-only during analysis. A future approval endpoint can apply an accepted patch; this first version intentionally stops at a proposal and evidence package.

## Implementation Phases

1. Build request and response schemas for a full fix run.
2. Add modular agents for repository scanning, error-log investigation, LLM-assisted repair planning, validation, and regression checks.
3. Add an orchestrator that records every stage, failure, and result in one traceable response.
4. Execute candidate edits and tests in a temporary copy of the supplied repository with a timeout and a restricted environment.
5. Expose the workflow through FastAPI and a dashboard where users can submit a repository path and bug report.
6. Add automated tests for health, validation rules, and the end-to-end fallback workflow.
7. Add an explicit human-approval endpoint that branches, applies reviewed edits, commits them, and returns the Git diff.

## Safety Controls

- The repository path must exist locally and contain a Git directory or source files.
- Test execution happens in a freshly copied temporary directory.
- Commands are allow-listed to pytest or Python's unittest runner and run with a timeout.
- The original repository is never changed by an analysis run.
- Generated fixes remain proposals until a human reviews and approves them.
- Candidate edits use exact search-and-replace operations in the disposable copy; an edit is rejected if its target is ambiguous or escapes the repository.

## Acceptance Criteria

- The API returns a structured debugging journey, root-cause analysis, patch proposal, test evidence, regression result, and PR summary.
- The dashboard can start a run and render its results.
- The application runs without an LLM key using a transparent heuristic fallback; with `OPENAI_API_KEY`, it requests a structured plan from an OpenAI-compatible model.
- Automated tests pass and the frontend builds successfully.
