# Sandbox Module (`backend/sandbox/`)

This package manages isolated Docker execution environments.

## Responsibilities
- Spinning up ephemeral containers with strict CPU/memory limits.
- Mounting source code volume mounts safely.
- Executing `pytest` commands inside the container sandbox.
- Capturing stdout, stderr, and test exit codes for validation agents.
