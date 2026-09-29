"""Repository auditor — scans source files for common bug patterns without requiring
the user to specify a file_path. Returns candidate_operations with file_path + line_number."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


# ── Pattern registry ─────────────────────────────────────────────────────────
# Each entry: (name, compiled_regex, category, build_replacement_fn)
# build_replacement_fn(line: str, match: re.Match) -> str

def _guard_division(line: str, m: re.Match) -> str:
    denominator = m.group("denom").strip()
    indent = len(line) - len(line.lstrip())
    pad = " " * indent
    return f"{pad}if {denominator} == 0:\n{pad}    return 0.0\n{line}"


def _safe_key_access(line: str, m: re.Match) -> str:
    obj = m.group("obj")
    key = m.group("key")
    quote = m.group("q")
    bad = f'{obj}[{quote}{key}{quote}]'
    safe = f'{obj}.get({quote}{key}{quote}, "<no-{key}>")'
    return line.replace(bad, safe, 1)


PATTERNS: list[dict[str, Any]] = [
    {
        "name": "bare_division",
        "regex": re.compile(
            r"(?P<lhs>.+?)\s*/\s*(?P<denom>[A-Za-z_]\w*)(?!\s*==|\s*!=|\s*<|\s*>|\s*is)"
        ),
        "categories": ["zerodivisionerror", "division by zero"],
        "description": "Division without a zero-denominator guard",
        "build_replacement": _guard_division,
    },
    {
        "name": "bare_dict_access",
        "regex": re.compile(
            r"(?P<obj>[A-Za-z_]\w*)\[(?P<q>['\"])(?P<key>[A-Za-z_]\w*)(?P=q)\]"
        ),
        "categories": ["keyerror", "missing key"],
        "description": "Direct dict key access without .get() fallback",
        "build_replacement": _safe_key_access,
    },
]


SOURCE_EXTENSIONS = {".py", ".js", ".ts", ".tsx"}


def audit_repository(
    repo_path: str,
    bug_description: str,
) -> list[dict[str, Any]]:
    """Scan *all* source files in repo_path for patterns related to bug_description.

    Returns a list of candidate_operation dicts with:
        file_path   – relative to repo_path (forward slashes)
        line_number – 1-indexed line where the pattern was found
        search      – exact line text (for context / display)
        replacement – suggested corrected line
        description – human-readable pattern name
    """
    repo = Path(repo_path).expanduser().resolve()
    if not repo.is_dir():
        raise ValueError(f"repository_path does not exist: {repo_path}")

    description_lower = bug_description.lower()

    # Select which patterns are relevant to this bug
    active_patterns = [
        p for p in PATTERNS
        if any(cat in description_lower for cat in p["categories"])
    ]

    if not active_patterns:
        # Generic fallback: return empty list; caller will use heuristic text
        return []

    operations: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()

    for source_file in repo.rglob("*"):
        if not source_file.is_file():
            continue
        if source_file.suffix not in SOURCE_EXTENSIONS:
            continue
        if ".git" in source_file.parts:
            continue
        if "test" in source_file.name.lower():
            # Skip test files — we audit production code
            continue

        try:
            lines = source_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue

        rel_path = source_file.relative_to(repo).as_posix()

        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            for pattern in active_patterns:
                m = pattern["regex"].search(stripped)
                if not m:
                    continue
                key = (rel_path, line_no)
                if key in seen:
                    continue
                seen.add(key)
                try:
                    replacement = pattern["build_replacement"](line, m)
                except Exception:
                    replacement = line  # safe fallback

                operations.append({
                    "file_path": rel_path,
                    "line_number": line_no,
                    "search": line,
                    "replacement": replacement,
                    "description": pattern["description"],
                })

    return operations
