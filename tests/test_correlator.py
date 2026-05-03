from src.correlator import feature_from_branch


def test_extracts_feature_from_feat_branch():
    assert feature_from_branch("feat/multi-agent-setup") == "multi-agent-setup"


def test_extracts_feature_from_fix_branch():
    assert feature_from_branch("fix/null-orgid") == "null-orgid"


def test_main_branch_returns_no_feature():
    assert feature_from_branch("main") == "_no-feature"


def test_staging_branch_returns_no_feature():
    assert feature_from_branch("staging") == "_no-feature"


def test_branch_without_prefix_returns_no_feature():
    assert feature_from_branch("random-branch") == "_no-feature"


def test_handles_all_conventional_types():
    types = [
        "feat",
        "fix",
        "chore",
        "refactor",
        "hotfix",
        "docs",
        "test",
        "perf",
        "build",
        "revert",
        "wip",
    ]
    for typ in types:
        assert feature_from_branch(f"{typ}/example") == "example"


def test_empty_branch_returns_no_feature():
    assert feature_from_branch("") == "_no-feature"


def test_nested_path_kept_intact():
    # branch can have nested slashes; we want everything after the type prefix
    assert feature_from_branch("feat/team/sub-feature") == "team/sub-feature"


# canonical_project tests


from src.correlator import canonical_project


def test_canonical_project_strips_worktrees_segment(tmp_path):
    # Simulate: ~/Developer/foo/.worktrees/bar should canonicalize to "foo"
    repo = tmp_path / "foo"
    repo.mkdir()
    import subprocess
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@test.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "test"],
        check=True,
    )
    (repo / "README.md").write_text("test\n")
    subprocess.run(
        ["git", "-C", str(repo), "add", "-A"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-q", "-m", "init"],
        check=True,
    )
    wt = repo / ".worktrees" / "bar"
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", "-q", "--detach", str(wt)],
        check=True,
    )
    assert canonical_project(str(wt)) == "foo"
    assert canonical_project(str(repo)) == "foo"


def test_canonical_project_returns_none_for_non_git(tmp_path):
    not_a_repo = tmp_path / "random-dir"
    not_a_repo.mkdir()
    assert canonical_project(str(not_a_repo)) is None


def test_canonical_project_returns_none_for_missing_path():
    assert canonical_project("/nonexistent/path/anywhere") is None


def test_canonical_project_returns_none_for_none_input():
    assert canonical_project(None) is None
    assert canonical_project("") is None


def test_canonical_project_preserves_hyphens_in_name(tmp_path):
    # Critical: "acme-tool" should stay "acme-tool", not become "acme/tool"
    repo = tmp_path / "acme-tool"
    repo.mkdir()
    import subprocess
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    assert canonical_project(str(repo)) == "acme-tool"


def test_canonical_project_strips_singular_worktree_marker(tmp_path):
    # Some repos use .worktree (singular) instead of .worktrees (plural)
    import subprocess
    repo = tmp_path / "ump"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t.com"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    (repo / "README.md").write_text("test\n")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True)
    wt = repo / ".worktree" / "feature-x"
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", "-q", "--detach", str(wt)],
        check=True,
    )
    assert canonical_project(str(wt)) == "ump"
