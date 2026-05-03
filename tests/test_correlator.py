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
