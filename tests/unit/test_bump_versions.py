"""Tests for genesis_os.tools.bump_versions."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path
import pytest

from genesis_os.tools import bump_versions as bv_module
from genesis_os.tools.bump_versions import (
    INIT_VERSION_RE,
    REPOS,
    VERSION_RE,
    bump_repo,
    main,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_file(tmp_path: Path) -> Path:
    """Return a fake __file__ path whose parents[5] == tmp_path."""
    # tmp_path/a/b/src/genesis_os/tools/bump_versions.py
    #   parents[0] = tmp_path/a/b/src/genesis_os/tools
    #   parents[5] = tmp_path
    fake = tmp_path / "a" / "b" / "src" / "genesis_os" / "tools" / "bump_versions.py"
    fake.parent.mkdir(parents=True, exist_ok=True)
    return fake


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_repos_count(self) -> None:
        assert len(REPOS) == 23

    def test_no_duplicate_repos(self) -> None:
        assert len(REPOS) == len(set(REPOS))

    def test_version_re_matches_pyproject(self) -> None:
        m = VERSION_RE.search('version = "0.1.0"')
        assert m is not None

    def test_version_re_captures_groups(self) -> None:
        result = VERSION_RE.sub(r'\g<1>0.3.0\g<2>', 'version = "0.1.0"', count=1)
        assert result == 'version = "0.3.0"'

    def test_init_version_re_matches(self) -> None:
        m = INIT_VERSION_RE.search('__version__ = "0.2.0"')
        assert m is not None

    def test_init_version_re_replaces(self) -> None:
        result = INIT_VERSION_RE.sub(r'\g<1>0.3.0\g<2>', '__version__ = "0.1.0"')
        assert result == '__version__ = "0.3.0"'


# ---------------------------------------------------------------------------
# bump_repo – pyproject.toml
# ---------------------------------------------------------------------------


class TestBumpRepoPyproject:
    def test_returns_false_when_dir_empty(self, tmp_path: Path) -> None:
        assert bump_repo(tmp_path, "0.3.0") is False

    def test_returns_true_when_version_bumped(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text('version = "0.2.0"\n', encoding="utf-8")
        assert bump_repo(tmp_path, "0.3.0") is True

    def test_new_version_written_to_pyproject(self, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('version = "0.2.0"\n', encoding="utf-8")
        bump_repo(tmp_path, "0.3.0")
        assert '"0.3.0"' in pyproject.read_text(encoding="utf-8")

    def test_returns_false_when_no_version_field(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "foo"\n', encoding="utf-8")
        assert bump_repo(tmp_path, "0.3.0") is False

    def test_preserves_other_content(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "foo"\nversion = "0.1.0"\n', encoding="utf-8"
        )
        bump_repo(tmp_path, "0.3.0")
        assert 'name = "foo"' in (tmp_path / "pyproject.toml").read_text(encoding="utf-8")

    def test_only_first_version_replaced(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text(
            'version = "0.1.0"\nother_version = "0.1.0"\n', encoding="utf-8"
        )
        bump_repo(tmp_path, "0.3.0")
        content = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
        assert content.count('"0.3.0"') == 1


# ---------------------------------------------------------------------------
# bump_repo – __init__.py
# ---------------------------------------------------------------------------


class TestBumpRepoInit:
    def _make_init(self, tmp_path: Path, content: str) -> Path:
        pkg = tmp_path / "src" / "mypkg"
        pkg.mkdir(parents=True)
        init = pkg / "__init__.py"
        init.write_text(content, encoding="utf-8")
        return init

    def test_bumps_version_in_init(self, tmp_path: Path) -> None:
        init = self._make_init(tmp_path, '__version__ = "0.2.0"\n')
        assert bump_repo(tmp_path, "0.3.0") is True
        assert '"0.3.0"' in init.read_text(encoding="utf-8")

    def test_returns_false_when_init_lacks_version(self, tmp_path: Path) -> None:
        self._make_init(tmp_path, "# no version here\n")
        assert bump_repo(tmp_path, "0.3.0") is False

    def test_bumps_both_pyproject_and_init(self, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('version = "0.2.0"\n', encoding="utf-8")
        init = self._make_init(tmp_path, '__version__ = "0.2.0"\n')
        assert bump_repo(tmp_path, "0.3.0") is True
        assert '"0.3.0"' in pyproject.read_text(encoding="utf-8")
        assert '"0.3.0"' in init.read_text(encoding="utf-8")

    def test_changed_true_from_init_alone(self, tmp_path: Path) -> None:
        # No pyproject.toml but init has version
        self._make_init(tmp_path, '__version__ = "0.1.0"\n')
        assert bump_repo(tmp_path, "0.2.0") is True


# ---------------------------------------------------------------------------
# main – validation
# ---------------------------------------------------------------------------


class TestMainValidation:
    def test_invalid_version_exits_with_1(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "argv", ["bump_versions", "not-semver"])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_invalid_version_prints_error(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["bump_versions", "bad"])
        with pytest.raises(SystemExit):
            main()
        assert "ERROR" in capsys.readouterr().out

    def test_version_with_v_prefix_is_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sys, "argv", ["bump_versions", "v0.3.0"])
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# main – repo discovery and bumping
# ---------------------------------------------------------------------------


class TestMainRepos:
    def test_default_version_0_2_0(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["bump_versions"])
        monkeypatch.setattr(bv_module, "__file__", str(_fake_file(tmp_path)))
        monkeypatch.setattr(bv_module, "REPOS", [])
        main()
        assert "0.2.0" in capsys.readouterr().out

    def test_missing_repos_go_to_skipped(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr(sys, "argv", ["bump_versions", "0.3.0"])
        monkeypatch.setattr(bv_module, "__file__", str(_fake_file(tmp_path)))
        monkeypatch.setattr(bv_module, "REPOS", ["nonexistent-repo"])
        main()
        assert "Skipped" in capsys.readouterr().out

    def test_updated_repo_printed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        repo_dir = tmp_path / "my-repo"
        repo_dir.mkdir()
        (repo_dir / "pyproject.toml").write_text('version = "0.2.0"\n', encoding="utf-8")

        monkeypatch.setattr(sys, "argv", ["bump_versions", "0.3.0"])
        monkeypatch.setattr(bv_module, "__file__", str(_fake_file(tmp_path)))
        monkeypatch.setattr(bv_module, "REPOS", ["my-repo"])
        main()
        out = capsys.readouterr().out
        assert "my-repo" in out
        assert "Updated" in out

    def test_repo_already_at_target_version_is_skipped(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        repo_dir = tmp_path / "my-repo"
        repo_dir.mkdir()
        (repo_dir / "pyproject.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")

        monkeypatch.setattr(sys, "argv", ["bump_versions", "0.3.0"])
        monkeypatch.setattr(bv_module, "__file__", str(_fake_file(tmp_path)))
        monkeypatch.setattr(bv_module, "REPOS", ["my-repo"])
        main()
        assert "Skipped" in capsys.readouterr().out

    def test_no_skipped_line_when_all_updated(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        repo_dir = tmp_path / "only-repo"
        repo_dir.mkdir()
        (repo_dir / "pyproject.toml").write_text('version = "0.2.0"\n', encoding="utf-8")

        monkeypatch.setattr(sys, "argv", ["bump_versions", "0.3.0"])
        monkeypatch.setattr(bv_module, "__file__", str(_fake_file(tmp_path)))
        monkeypatch.setattr(bv_module, "REPOS", ["only-repo"])
        main()
        out = capsys.readouterr().out
        assert "Skipped" not in out
        assert "Next:" in out

    def test_updated_count_in_output(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        for name in ["repo-a", "repo-b"]:
            d = tmp_path / name
            d.mkdir()
            (d / "pyproject.toml").write_text('version = "0.1.0"\n', encoding="utf-8")

        monkeypatch.setattr(sys, "argv", ["bump_versions", "0.2.0"])
        monkeypatch.setattr(bv_module, "__file__", str(_fake_file(tmp_path)))
        monkeypatch.setattr(bv_module, "REPOS", ["repo-a", "repo-b"])
        main()
        out = capsys.readouterr().out
        assert "Updated : 2" in out


# ---------------------------------------------------------------------------
# __main__ entry-point
# ---------------------------------------------------------------------------


class TestMainEntryPoint:
    def test_entry_point_runs_without_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # runpy re-executes the module in a fresh namespace (so patches on the
        # existing module object don't apply).  Set argv to a valid version and
        # ensure no repos exist → all skipped, no error raised.
        monkeypatch.setattr(sys, "argv", ["bump_versions", "0.3.0"])
        runpy.run_module("genesis_os.tools.bump_versions", run_name="__main__")
