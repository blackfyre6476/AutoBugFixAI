from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import httpx


class RepositoryAnalyst:
    name = "Repository Analyst"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        repo = Path(context["repository_path"])
        files = [p for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts]
        source_files = [p for p in files if p.suffix in {".py", ".js", ".ts", ".tsx"}]
        tests = [p for p in source_files if "test" in p.name.lower() or "tests" in p.parts]
        context["source_files"] = source_files[:250]
        context["test_files"] = tests[:100]
        return {
            "summary": f"Scanned {len(source_files)} source files and found {len(tests)} test files.",
            "files": [str(p.relative_to(repo)) for p in source_files[:30]],
        }


class BugInvestigator:
    name = "Bug Investigator"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        report = context["bug_description"]
        repo = Path(context["repository_path"])
        candidates: list[str] = []

        # Separate production files from test files
        all_source = context["source_files"]
        prod_files = [p for p in all_source if "test" not in p.name.lower() and "tests" not in p.parts]
        test_files_list = [p for p in all_source if p not in prod_files]

        # First: match file names from stack trace references
        trace_paths = re.findall(r'File ["\']([^"\']+)', report)
        for trace_path in trace_paths:
            match = next((p for p in all_source if p.name == Path(trace_path).name), None)
            if match:
                relative = str(match.relative_to(repo))
                if relative not in candidates:
                    candidates.append(relative)

        keywords = set(re.findall(r"[A-Za-z_]{4,}", report.lower()))

        # Search production files first (lower threshold — 1 keyword match is enough)
        for path in prod_files:
            if len(candidates) >= 8:
                break
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                continue
            if sum(word in text for word in keywords) >= 1:
                relative = str(path.relative_to(repo))
                if relative not in candidates:
                    candidates.append(relative)

        # If no production file matched, fall back to test files
        if not candidates:
            for path in test_files_list:
                if len(candidates) >= 8:
                    break
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore").lower()
                except OSError:
                    continue
                if sum(word in text for word in keywords) >= 2:
                    relative = str(path.relative_to(repo))
                    if relative not in candidates:
                        candidates.append(relative)

        cause = "The report was correlated with the listed source files; inspect the proposed guard and its affected call path."
        if "zerodivisionerror" in report.lower() or "division by zero" in report.lower():
            cause = "An arithmetic operation accepts a zero denominator without a defined fallback or validation guard."
        elif "keyerror" in report.lower() or "missing key" in report.lower():
            cause = "A direct dictionary key access fails when the key is absent; replace with .get() and a safe fallback value."
        return {"affected_files": candidates, "root_cause": cause}


class FixGenerator:
    name = "Fix Generator"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            prompt = {
                "role": "You are a cautious software engineer. Return JSON with root_cause, proposed_fix, patch_preview, and candidate_operations. candidate_operations is a list of {file_path, line_number, search, replacement}; specify file_path and line_number (1-indexed) for every code edit. Never use absolute paths.",
                "repository_files": context.get("analysis_files", []),
                "affected_files": context.get("affected_files", []),
                "bug_report": context["bug_description"],
            }
            try:
                async with httpx.AsyncClient(timeout=25) as client:
                    response = await client.post(
                        os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}"},
                        json={"model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"), "messages": [{"role": "user", "content": json.dumps(prompt)}], "response_format": {"type": "json_object"}},
                    )
                    response.raise_for_status()
                    payload = json.loads(response.json()["choices"][0]["message"]["content"])
                    operations = payload.get("candidate_operations", [])
                    if not isinstance(operations, list):
                        operations = []
                    return {**payload, "candidate_operations": operations, "llm_mode": "openai_compatible"}
            except (httpx.HTTPError, KeyError, json.JSONDecodeError):
                pass

        is_zero_division = "zerodivisionerror" in context["bug_description"].lower() or "division by zero" in context["bug_description"].lower()
        is_key_error = "keyerror" in context["bug_description"].lower() or "missing key" in context["bug_description"].lower()

        if is_zero_division:
            fix = "Validate the denominator before division and return the domain-approved fallback (or raise a clear validation error). Add a test for a zero denominator."
            patch = "# Proposed change\nif denominator == 0:\n    return 0.0  # replace with the product's documented fallback\nreturn numerator / denominator"
        elif is_key_error:
            fix = "Replace direct dict key access (dict['key']) with dict.get('key', fallback) to handle missing keys gracefully."
            patch = "# Proposed change\nvalue = data.get('key', '<fallback>')"
        else:
            fix = "Add a narrowly scoped guard around the failing input and cover the reported behavior with a regression test before applying the change."
            patch = "# Patch proposal requires LLM review or a more specific stack trace.\n# Add a regression test reproducing the supplied failure."

        # ── Heuristic source scan ──────────────────────────────────────────────
        candidate_operations: list[dict] = []
        repo = Path(context["repository_path"])
        affected_files = context.get("affected_files", [])

        division_pattern = re.compile(r"(.+?)\s*/\s*(\w+)")
        key_access_pattern = re.compile(r"\w+\[['\"](\w+)['\"]\]")

        # Only scan production (non-test) files;
        # if investigator found no production files, fall back to all source files
        scan_rel_paths = [f for f in affected_files if "test" not in Path(f).name.lower()]
        if not scan_rel_paths:
            all_source: list[Path] = context.get("source_files", [])
            scan_rel_paths = [
                str(p.relative_to(repo))
                for p in all_source
                if "test" not in p.name.lower() and "tests" not in p.parts and p.is_file()
            ]

        for rel_path in scan_rel_paths:
            target = repo / rel_path
            if not target.is_file():
                continue
            try:
                source_lines = target.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue
            for line_no, line in enumerate(source_lines, start=1):
                stripped = line.strip()
                # Skip comments and blank lines
                if not stripped or stripped.startswith("#"):
                    continue
                if is_zero_division and "/" in stripped and not stripped.startswith(("if ", "return 0", "#")):
                    m = division_pattern.search(stripped)
                    if m:
                        denom = m.group(2).strip()
                        indent = len(line) - len(line.lstrip())
                        pad = " " * indent
                        candidate_operations.append({
                            "file_path": rel_path,
                            "line_number": line_no,
                            "search": line,
                            "replacement": (
                                f"{pad}if {denom} == 0:\n"
                                f"{pad}    return 0.0\n"
                                f"{line}"
                            ),
                        })
                        break  # one candidate per file for heuristic
                elif is_key_error:
                    km = re.search(r"(\w+)\[(['\"])(\w+)\2\]", stripped)
                    if km:
                        obj, key = km.group(1), km.group(3)
                        bad_access = km.group(0)
                        safe_access = f'{obj}.get("{key}", "<no-{key}>")'
                        new_line = line.replace(bad_access, safe_access, 1)
                        candidate_operations.append({
                            "file_path": rel_path,
                            "line_number": line_no,
                            "search": line,
                            "replacement": new_line,
                        })
                        break

        return {
            "root_cause": context["root_cause"],
            "proposed_fix": fix,
            "patch_preview": patch,
            "candidate_operations": candidate_operations,
            "llm_mode": "heuristic_fallback",
        }
