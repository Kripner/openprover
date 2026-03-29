"""Lean 4 integration - parsing, assembly, verification, file management."""

import logging
import re
import secrets
import subprocess
from pathlib import Path

logger = logging.getLogger("openprover.lean")

# Matches Lean 4 diagnostic lines like "6:8: error ..." (after file path stripping)
_LEAN_ERROR_RE = re.compile(r"^\d+:\d+: error", re.MULTILINE)


def lean_has_errors(feedback: str) -> bool:
    """Return True if feedback contains Lean error diagnostics (not just warnings/info)."""
    return bool(_LEAN_ERROR_RE.search(feedback))


# Matches ```lean ... ``` or ```  ... ``` code fences (with optional language tag)
_CODE_FENCE_RE = re.compile(
    r"^\s*```\w*\s*\n(.*?)^\s*```\s*$",
    re.MULTILINE | re.DOTALL,
)
# Matches <code>...</code> or <code lang="lean">...</code>
_CODE_TAG_RE = re.compile(
    r"<code(?:\s[^>]*)?>(.+?)</code>",
    re.DOTALL,
)


def strip_code_fences(code: str) -> str:
    """Strip markdown code fences or HTML code tags from LLM-generated code.

    Models sometimes wrap tool arguments in ```lean ... ```, <code>...</code>,
    or similar. This extracts the inner content, or returns the original if
    no wrapping found.
    """
    m = _CODE_FENCE_RE.search(code)
    if m:
        return m.group(1)
    m = _CODE_TAG_RE.search(code)
    if m:
        return m.group(1)
    return code


class LeanTheorem:
    """Parsed representation of a THEOREM.lean file with sorry placeholders."""

    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.preamble_end = 0  # byte offset where preamble ends
        self.sorry_positions: list[tuple[int, int]] = []  # (start, end) for each sorry
        self.num_sorries = 0
        self._parse()

    def _parse(self):
        # Find preamble end: import/open/set_option lines + blanks/comments at top
        lines = self.raw_text.split('\n')
        preamble_end_line = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (stripped.startswith('import ') or stripped.startswith('open ')
                    or stripped == '' or stripped.startswith('--')):
                preamble_end_line = i + 1
            else:
                break
        # Convert line index to byte offset
        self.preamble_end = sum(len(lines[j]) + 1 for j in range(preamble_end_line))

        # Find all sorry positions (word boundary match)
        self.sorry_positions = [
            (m.start(), m.end())
            for m in re.finditer(r'\bsorry\b', self.raw_text)
        ]
        self.num_sorries = len(self.sorry_positions)

    def assemble_proof(self, replacements: list[str], context: str = "") -> str:
        """Replace each sorry with corresponding replacement block.

        Args:
            replacements: N strings, one per sorry in order.
            context: Optional block inserted after preamble (imports/opens).

        Returns:
            Complete lean file with sorries replaced.

        Raises:
            ValueError: wrong number of replacements, or import in injected code.
        """
        if len(replacements) != self.num_sorries:
            raise ValueError(
                f"Expected {self.num_sorries} replacement(s), got {len(replacements)}"
            )

        # Validate no imports in injected code
        for i, block in enumerate(replacements):
            if re.search(r'^\s*import\b', block, re.MULTILINE):
                raise ValueError(
                    f"Replacement block {i} contains an import statement"
                )
        if context and re.search(r'^\s*import\b', context, re.MULTILINE):
            raise ValueError("Context block contains an import statement")

        # Replace sorries in reverse order (preserves earlier offsets)
        result = self.raw_text
        for (start, end), replacement in reversed(
            list(zip(self.sorry_positions, replacements))
        ):
            result = result[:start] + replacement + result[end:]

        # Inject context after preamble
        if context:
            result = (result[:self.preamble_end]
                      + context + '\n'
                      + result[self.preamble_end:])

        return result


def run_lean_check(lean_file: Path, project_dir: Path,
                   timeout: int = 300) -> tuple[bool, str, str]:
    """Run ``lake env lean <file>`` and return (success, feedback, cmd_info).

    Success means returncode 0 and empty stdout.
    cmd_info is a human-readable string with the exact command and cwd.
    """
    cmd = ["lake", "env", "lean", str(lean_file.resolve())]
    cwd = str(project_dir)
    cmd_info = f"cwd: {cwd}\ncmd: {' '.join(cmd)}"
    logger.info("Verifying %s", lean_file.name)
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        if proc.returncode == 0 and not stdout:
            logger.info("Lean check passed: %s", lean_file.name)
            return (True, "", cmd_info)

        parts = []
        if stdout:
            parts.append(stdout)
        if stderr:
            parts.append(stderr)
        feedback = '\n'.join(parts)
        # Strip the full file path prefix from each diagnostic line
        file_prefix = str(lean_file.resolve()) + ":"
        feedback = '\n'.join(
            line[len(file_prefix):] if line.startswith(file_prefix) else line
            for line in feedback.splitlines()
        )
        logger.info("Lean check failed: %s", lean_file.name)
        return (False, feedback, cmd_info)

    except subprocess.TimeoutExpired:
        logger.warning("Lean verification timed out: %s (%ds)", lean_file.name, timeout)
        return (False, f"Lean verification timed out after {timeout}s", cmd_info)
    except FileNotFoundError:
        logger.error("lake command not found")
        return (False, "lake command not found - is Lean/Lake installed and on PATH?", cmd_info)


def merge_lean_imports(existing: str, new_snippet: str) -> str:
    """Merge two Lean code blocks, deduplicating imports at the top."""
    import_lines: list[str] = []
    seen_imports: set[str] = set()
    body_existing: list[str] = []
    body_new: list[str] = []

    for line in existing.splitlines():
        stripped = line.strip()
        if stripped.startswith("import "):
            if stripped not in seen_imports:
                seen_imports.add(stripped)
                import_lines.append(line)
        else:
            body_existing.append(line)

    for line in new_snippet.splitlines():
        stripped = line.strip()
        if stripped.startswith("import "):
            if stripped not in seen_imports:
                seen_imports.add(stripped)
                import_lines.append(line)
        else:
            body_new.append(line)

    # Ensure two blank lines before the new block
    if body_existing and body_new:
        # Strip trailing blank lines from existing, then add two
        while body_existing and body_existing[-1].strip() == '':
            body_existing.pop()
        body_existing.append('')
        body_existing.append('')
    return '\n'.join(import_lines + body_existing + body_new)


class LeanWorkDir:
    """Manages the OpenProver-{id} subdirectory within a Lean project."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.random_id = secrets.token_hex(4)  # 8 hex chars
        self.dir = project_dir / f"OpenProver-{self.random_id}"
        self.dir.mkdir(parents=True, exist_ok=True)

    def make_file(self, slug: str, content: str, ext: str = ".lean") -> Path:
        """Write a file with slug-based name + random suffix."""
        suffix = secrets.token_hex(3)  # 6 hex chars
        flat_slug = slug.replace("/", "_")
        path = self.dir / f"{flat_slug}-{suffix}{ext}"
        path.write_text(content)
        return path

    def write_proof(self, content: str) -> Path:
        """Write the final PROOF.lean."""
        path = self.dir / "PROOF.lean"
        path.write_text(content)
        return path
