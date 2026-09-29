# Backend Agents Module (`backend/agents/`)

This package contains the AI agents responsible for autonomous software engineering tasks.

## Planned Agents (Phase 2 & Phase 3)

1. **Repository Analyst Agent** (`repository_analyst.py`)
   - Parses AST and dependency structures of the codebase.
   - Extracts functions, classes, unit test paths, and configuration files.

2. **Bug Investigator Agent** (`bug_investigator.py`)
   - Analyzes error logs / bug reports against repository AST index.
   - Pinpoints suspicious files, stack trace frames, and target code locations.

3. **Fix Generator Agent** (`fix_generator.py`)
   - Uses Gemini API to produce context-aware code diffs and patches.

4. **Validation Agent** (`validation_agent.py`)
   - Runs target unit tests in the Docker sandbox to verify bug resolution.

5. **Regression Agent** (`regression_agent.py`)
   - Executes the full test suite in the Docker sandbox to prevent breaking existing functionality.
