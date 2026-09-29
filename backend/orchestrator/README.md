# Orchestrator Module (`backend/orchestrator/`)

This package manages the lifecycle of an AutoFix AI bug-fixing job.

## Workflow Pipeline State Machine

```
[ Ingest Request ] ➔ [ 1. Repo Clone ] ➔ [ 2. Repo Analyst ]
                                                  │
                                                  ▼
[ 5. PR Summary ] ◄─ [ 4. Sandbox Validation ] ◄─ [ 3. Fix Generator ]
```
