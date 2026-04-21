"""Tests for genesis_os.sigillin — SigillinSync trilayer protocol."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from genesis_os.sigillin import SigillinSync


class TestSigillinSync:
    def setup_method(self) -> None:
        self.sync = SigillinSync()

    # --- check_trilayer ---

    def test_check_nonexistent_path(self) -> None:
        result = self.sync.check_trilayer(Path("/nonexistent/path"))
        assert result["gaps"] == 0
        assert result["total_concepts"] == 0

    def test_check_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.sync.check_trilayer(Path(tmpdir))
            assert result["gaps"] == 0
            assert result["total_concepts"] == 0

    def test_check_complete_trilayer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            for ext in ("yaml", "json", "md"):
                (base / f"utac_bridge.{ext}").write_text(f"test {ext}")
            result = self.sync.check_trilayer(base)
            assert result["gaps"] == 0
            assert "utac_bridge" in result["complete"]

    def test_check_missing_one_extension(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "afet.yaml").write_text("test")
            (base / "afet.json").write_text("{}")
            # missing .md
            result = self.sync.check_trilayer(base)
            assert result["gaps"] == 1
            assert len(result["missing"]) == 1
            assert "md" in result["missing"][0]

    def test_check_multiple_concepts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Complete concept
            for ext in ("yaml", "json", "md"):
                (base / f"complete.{ext}").write_text("test")
            # Incomplete concept
            (base / "incomplete.yaml").write_text("test")
            result = self.sync.check_trilayer(base)
            assert result["gaps"] == 1
            assert "complete" in result["complete"]

    # --- generate_trilayer ---

    def test_generate_creates_all_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            content = {
                "beta": 7.4,
                "domain": "biological",
                "description": "UTAC β for biological systems.",
            }
            written = self.sync.generate_trilayer(content, base, "test_concept")
            assert "yaml" in written
            assert "json" in written
            assert "md" in written
            for ext, path in written.items():
                assert Path(path).exists()

    def test_generate_json_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            content = {"beta": 7.4, "description": "Test."}
            written = self.sync.generate_trilayer(content, base, "bio_params")
            with open(written["json"]) as f:
                data = json.load(f)
            assert data["beta"] == pytest.approx(7.4)

    def test_generate_md_contains_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            content = {"beta": 11.0, "description": "Climate β parameter."}
            written = self.sync.generate_trilayer(content, base, "climate_params")
            md = Path(written["md"]).read_text()
            assert "Climate Params" in md
            assert "Climate β parameter." in md

    def test_generate_creates_subdirectory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir) / "subdir" / "nested"
            content = {"key": "value", "description": "Nested dir test."}
            written = self.sync.generate_trilayer(content, base, "nested_concept")
            assert base.exists()
            for path in written.values():
                assert Path(path).exists()

    # --- validate_concept ---

    def test_validate_all_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            for ext in ("yaml", "json", "md"):
                (base / f"crep.{ext}").write_text("test")
            result = self.sync.validate_concept("crep", base)
            assert all(result.values())

    def test_validate_some_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "partial.yaml").write_text("test")
            result = self.sync.validate_concept("partial", base)
            assert result["yaml"] is True
            assert result["json"] is False
            assert result["md"] is False

    # --- is_complete ---

    def test_is_complete_true(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            for ext in ("yaml", "json", "md"):
                (base / f"utac.{ext}").write_text("x")
            assert self.sync.is_complete("utac", base) is True

    def test_is_complete_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "utac.yaml").write_text("x")
            assert self.sync.is_complete("utac", base) is False

    # --- round-trip ---

    def test_generate_then_check_no_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            content = {"param": "value", "description": "Full concept."}
            self.sync.generate_trilayer(content, base, "full_concept")
            result = self.sync.check_trilayer(base)
            assert result["gaps"] == 0

    # --- custom extensions ---

    def test_custom_extensions(self) -> None:
        sync = SigillinSync(extensions=("json", "md"))
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "concept.json").write_text("{}")
            (base / "concept.md").write_text("# Concept")
            result = sync.check_trilayer(base)
            assert result["gaps"] == 0
