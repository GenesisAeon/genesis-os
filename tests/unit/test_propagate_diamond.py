"""Tests for genesis_os.tools.propagate_diamond."""
from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from genesis_os.tools.propagate_diamond import (
    BRANCH,
    COMMIT_MSG,
    ORG,
    REPOS,
    TEMPLATE_FILES,
    TEMPLATES_DIR,
    _copy_templates,
    _merge_pyproject,
    _run,
    main,
    propagate,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_repos_count(self):
        assert len(REPOS) == 23

    def test_template_files_keys(self):
        assert ".github/workflows/ci.yml" in TEMPLATE_FILES
        assert ".github/workflows/release.yml" in TEMPLATE_FILES
        assert "README_QUICKSTART.md" in TEMPLATE_FILES

    def test_templates_dir_exists(self):
        assert TEMPLATES_DIR.is_dir()

    def test_template_files_exist(self):
        for src in TEMPLATE_FILES.values():
            assert (TEMPLATES_DIR / src).exists(), f"Template missing: {src}"

    def test_org(self):
        assert ORG == "GenesisAeon"

    def test_branch(self):
        assert BRANCH == "feat/diamond-propagation"

    def test_commit_msg_non_empty(self):
        assert len(COMMIT_MSG) > 0

    def test_no_duplicate_repos(self):
        assert len(REPOS) == len(set(REPOS))


# ---------------------------------------------------------------------------
# _run
# ---------------------------------------------------------------------------


class TestRun:
    def test_calls_subprocess_with_cwd(self, tmp_path):
        with patch("subprocess.run") as mock_run:
            _run(["git", "status"], cwd=tmp_path)
        mock_run.assert_called_once_with(
            ["git", "status"], cwd=tmp_path, check=True, text=True
        )

    def test_calls_subprocess_without_cwd(self):
        with patch("subprocess.run") as mock_run:
            _run(["git", "status"])
        mock_run.assert_called_once_with(
            ["git", "status"], cwd=None, check=True, text=True
        )

    def test_propagates_called_process_error(self, tmp_path):
        with (
            patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "git")),
            pytest.raises(subprocess.CalledProcessError),
        ):
            _run(["git", "fail"], cwd=tmp_path)


# ---------------------------------------------------------------------------
# _copy_templates
# ---------------------------------------------------------------------------


class TestCopyTemplates:
    def test_creates_workflow_dirs(self, tmp_path):
        _copy_templates(tmp_path)
        assert (tmp_path / ".github" / "workflows" / "ci.yml").exists()
        assert (tmp_path / ".github" / "workflows" / "release.yml").exists()

    def test_copies_quickstart(self, tmp_path):
        _copy_templates(tmp_path)
        assert (tmp_path / "README_QUICKSTART.md").exists()

    def test_content_matches_source(self, tmp_path):
        _copy_templates(tmp_path)
        for target, source in TEMPLATE_FILES.items():
            expected = (TEMPLATES_DIR / source).read_text()
            actual = (tmp_path / target).read_text()
            assert actual == expected

    def test_overwrites_existing_file(self, tmp_path):
        ci_path = tmp_path / ".github" / "workflows" / "ci.yml"
        ci_path.parent.mkdir(parents=True, exist_ok=True)
        ci_path.write_text("old content")
        _copy_templates(tmp_path)
        assert ci_path.read_text() != "old content"


# ---------------------------------------------------------------------------
# _merge_pyproject
# ---------------------------------------------------------------------------


class TestMergePyproject:
    def test_no_pyproject_does_nothing(self, tmp_path):
        # Must not raise when pyproject.toml is absent
        _merge_pyproject(tmp_path, "test-repo")

    def test_already_has_urls_unchanged(self, tmp_path):
        pyproject = tmp_path / "pyproject.toml"
        original = "[project.urls]\nHomepage = 'http://example.com'\n"
        pyproject.write_text(original)
        _merge_pyproject(tmp_path, "test-repo")
        assert pyproject.read_text() == original

    def test_adds_urls_section(self, tmp_path):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'\n")
        _merge_pyproject(tmp_path, "my-repo")
        content = pyproject.read_text()
        assert "[project.urls]" in content

    def test_adds_repo_name(self, tmp_path):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'\n")
        _merge_pyproject(tmp_path, "my-repo")
        assert "my-repo" in pyproject.read_text()

    def test_adds_zenodo_placeholder(self, tmp_path):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'\n")
        _merge_pyproject(tmp_path, "my-repo")
        content = pyproject.read_text().lower()
        assert "zenodo" in content

    def test_preserves_original_content(self, tmp_path):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'\n")
        _merge_pyproject(tmp_path, "my-repo")
        assert pyproject.read_text().startswith("[project]\nname = 'test'\n")


# ---------------------------------------------------------------------------
# propagate
# ---------------------------------------------------------------------------


class TestPropagate:
    def test_clones_when_repo_missing(self, tmp_path):
        with (
            patch("genesis_os.tools.propagate_diamond._run") as mock_run,
            patch("genesis_os.tools.propagate_diamond._copy_templates"),
            patch("genesis_os.tools.propagate_diamond._merge_pyproject"),
        ):
            propagate("new-repo", tmp_path)
        cmd_lists = [c.args[0] for c in mock_run.call_args_list]
        assert any("clone" in cmd for cmd in cmd_lists)

    def test_pulls_when_repo_exists(self, tmp_path):
        (tmp_path / "existing-repo").mkdir()
        with (
            patch("genesis_os.tools.propagate_diamond._run") as mock_run,
            patch("genesis_os.tools.propagate_diamond._copy_templates"),
            patch("genesis_os.tools.propagate_diamond._merge_pyproject"),
        ):
            propagate("existing-repo", tmp_path)
        cmd_lists = [c.args[0] for c in mock_run.call_args_list]
        assert any("pull" in cmd for cmd in cmd_lists)
        assert not any("clone" in cmd for cmd in cmd_lists)

    def test_commits_changes(self, tmp_path):
        with (
            patch("genesis_os.tools.propagate_diamond._run") as mock_run,
            patch("genesis_os.tools.propagate_diamond._copy_templates"),
            patch("genesis_os.tools.propagate_diamond._merge_pyproject"),
        ):
            propagate("new-repo", tmp_path)
        cmd_lists = [c.args[0] for c in mock_run.call_args_list]
        assert any("commit" in cmd for cmd in cmd_lists)

    def test_pushes_to_branch(self, tmp_path):
        with (
            patch("genesis_os.tools.propagate_diamond._run") as mock_run,
            patch("genesis_os.tools.propagate_diamond._copy_templates"),
            patch("genesis_os.tools.propagate_diamond._merge_pyproject"),
        ):
            propagate("new-repo", tmp_path)
        cmd_lists = [c.args[0] for c in mock_run.call_args_list]
        assert any("push" in cmd for cmd in cmd_lists)
        all_args_flat = " ".join(str(a) for cmd in cmd_lists for a in cmd)
        assert BRANCH in all_args_flat

    def test_uses_org_in_clone_url(self, tmp_path):
        with (
            patch("genesis_os.tools.propagate_diamond._run") as mock_run,
            patch("genesis_os.tools.propagate_diamond._copy_templates"),
            patch("genesis_os.tools.propagate_diamond._merge_pyproject"),
        ):
            propagate("new-repo", tmp_path)
        all_args_flat = " ".join(
            str(a) for c in mock_run.call_args_list for a in c.args[0]
        )
        assert ORG in all_args_flat

    def test_calls_copy_templates(self, tmp_path):
        with (
            patch("genesis_os.tools.propagate_diamond._run"),
            patch("genesis_os.tools.propagate_diamond._copy_templates") as mock_copy,
            patch("genesis_os.tools.propagate_diamond._merge_pyproject"),
        ):
            propagate("new-repo", tmp_path)
        mock_copy.assert_called_once_with(tmp_path / "new-repo")

    def test_calls_merge_pyproject(self, tmp_path):
        with (
            patch("genesis_os.tools.propagate_diamond._run"),
            patch("genesis_os.tools.propagate_diamond._copy_templates"),
            patch("genesis_os.tools.propagate_diamond._merge_pyproject") as mock_merge,
        ):
            propagate("new-repo", tmp_path)
        mock_merge.assert_called_once_with(tmp_path / "new-repo", "new-repo")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


class TestMain:
    def test_calls_propagate_for_all_repos(self):
        with patch("genesis_os.tools.propagate_diamond.propagate") as mock_propagate:
            main()
        assert mock_propagate.call_count == len(REPOS)

    def test_passes_repo_name_to_propagate(self):
        with patch("genesis_os.tools.propagate_diamond.propagate") as mock_propagate:
            main()
        called_repos = [c.args[0] for c in mock_propagate.call_args_list]
        assert set(called_repos) == set(REPOS)

    def test_continues_after_error(self):
        call_count = 0

        def side_effect(repo: str, base_dir: Path) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise subprocess.CalledProcessError(1, "git")

        with patch("genesis_os.tools.propagate_diamond.propagate", side_effect=side_effect):
            main()  # Must not raise

        assert call_count == len(REPOS)

    def test_reports_failed_repos(self, capsys):
        def side_effect(repo: str, base_dir: Path) -> None:
            if repo == REPOS[0]:
                raise ValueError("simulated failure")

        with patch("genesis_os.tools.propagate_diamond.propagate", side_effect=side_effect):
            main()

        output = capsys.readouterr().out
        assert "Failed" in output or "Error" in output

    def test_reports_success_count(self, capsys):
        with patch("genesis_os.tools.propagate_diamond.propagate"):
            main()
        output = capsys.readouterr().out
        assert f"{len(REPOS)}/{len(REPOS)}" in output

    def test_no_failed_section_on_clean_run(self, capsys):
        with patch("genesis_os.tools.propagate_diamond.propagate"):
            main()
        output = capsys.readouterr().out
        assert "Failed:" not in output
