"""Patch application logic for AutoFix AI supporting file_path, line_number, search, and replacement."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def apply_patch_operation(text: str, operation: dict[str, Any], file_path: str) -> str:
    """Apply a single patch operation to string text.
    
    Supports:
    - line_number (1-indexed) with optional search string or direct line replacement.
    - search string matching when line_number is not provided.
    """
    line_number = operation.get("line_number")
    search = operation.get("search", "")
    replacement = operation.get("replacement", "")

    if line_number is not None:
        lines = text.splitlines(keepends=True)
        total_lines = len(lines)
        if not (1 <= line_number <= total_lines + 1):
            raise ValueError(f"Line number {line_number} is out of bounds for {file_path} (file has {total_lines} lines).")
        
        idx = line_number - 1

        if search:
            search_lines = search.splitlines()
            num_search = len(search_lines) or 1
            
            # Check if search matches at exact line_number
            target_chunk = "".join(lines[idx : idx + num_search])
            if target_chunk.rstrip("\r\n") == search.rstrip("\r\n"):
                match_idx = idx
            else:
                # Search within a ±3 line window around line_number for slight offsets
                match_idx = None
                window_start = max(0, idx - 3)
                window_end = min(total_lines, idx + 4)
                for test_idx in range(window_start, window_end):
                    chunk = "".join(lines[test_idx : test_idx + num_search])
                    if chunk.rstrip("\r\n") == search.rstrip("\r\n"):
                        match_idx = test_idx
                        break
                
                if match_idx is None:
                    raise ValueError(f"Expected search block near line {line_number} in {file_path}; content did not match.")

            # Replace lines at match_idx
            prefix = lines[:match_idx]
            suffix = lines[match_idx + len(search_lines):]
            rep_text = replacement if replacement.endswith("\n") or not suffix else replacement + "\n"
            return "".join(prefix) + rep_text + "".join(suffix)
        else:
            # Direct line replacement at line_number
            prefix = lines[:idx]
            suffix = lines[idx + 1:] if idx < total_lines else []
            rep_text = replacement if replacement.endswith("\n") or not suffix else replacement + "\n"
            return "".join(prefix) + rep_text + "".join(suffix)

    # Fallback to search-based replacement when line_number is None
    if not search:
        raise ValueError(f"Either line_number or non-empty search string must be provided for {file_path}.")

    occurrences = text.count(search)
    if occurrences == 0:
        raise ValueError(f"Search block not found in {file_path}.")
    if occurrences > 1:
        raise ValueError(f"Expected exactly one matching code block in {file_path}; found {occurrences}. Please specify line_number.")

    return text.replace(search, replacement, 1)


def apply_patch_operations(root: Path, operations: list[dict[str, Any]]) -> tuple[bool, str]:
    """Apply a list of patch operations to files under root directory."""
    if not operations:
        return False, "No candidate patch was supplied; baseline tests only."

    for operation in operations:
        file_path = operation.get("file_path", "")
        if not file_path:
            return False, "Patch operation missing file_path."

        path = (root / file_path).resolve()
        if root not in path.parents or not path.is_file():
            return False, f"Patch file is outside the target repository or missing: {file_path}"

        text = path.read_text(encoding="utf-8")
        try:
            new_text = apply_patch_operation(text, operation, file_path)
            path.write_text(new_text, encoding="utf-8")
        except ValueError as exc:
            return False, str(exc)

    return True, f"Applied {len(operations)} candidate edit(s) to the workspace."
