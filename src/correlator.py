"""Correlate sessions to features and PRs.

A session's "feature" is parsed from the worktree branch name following the
project's Conventional Commits convention. Optional ``gh`` CLI lookup enriches
features with PR data when available.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Optional

_CONVENTIONAL = re.compile(
    r"^(feat|fix|chore|refactor|hotfix|docs|test|perf|build|revert|wip)/(.+)$"
)


def feature_from_branch(branch: str) -> str:
    """Extract feature name from a Conventional Commits branch.

    ``feat/foo`` -> ``foo``. ``main``, ``staging``, or non-conventional names
    return the sentinel ``_no-feature`` (prefix ``_`` to group these in UIs).
    """
    m = _CONVENTIONAL.match(branch or "")
    return m.group(2) if m else "_no-feature"


def branch_for_worktree(worktree_path: Path) -> Optional[str]:
    """Return the current branch of a git worktree, or None if not a git repo."""
    try:
        out = subprocess.check_output(
            ["git", "-C", str(worktree_path), "branch", "--show-current"],
            stderr=subprocess.DEVNULL,
            timeout=2,
        )
        branch = out.decode().strip()
        return branch or None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None


def find_pr_for_branch(repo_path: Path, branch: str) -> Optional[dict]:
    """Look up an open or recently-closed PR for a branch via ``gh`` CLI.

    Returns a dict with at least ``number``, ``url``, ``state`` if found.
    Returns ``None`` if ``gh`` is unavailable, unauthenticated, or no PR exists.
    """
    try:
        out = subprocess.check_output(
            [
                "gh",
                "pr",
                "list",
                "--head",
                branch,
                "--state",
                "all",
                "--json",
                "number,url,state",
                "--jq",
                ".[0]",
            ],
            cwd=str(repo_path),
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        text = out.decode().strip()
        if not text or text == "null":
            return None
        return json.loads(text)
    except Exception:
        return None
