"""Tests for safe release-tag parsing."""

from __future__ import annotations

import pytest

from genesis_os.tools.release_version import parse_release_tag


@pytest.mark.parametrize(
    ("tag", "expected"),
    [
        ("v1.0.2", "1.0.2"),
        ("v1.1.0", "1.1.0"),
        ("v2.1.0", "2.1.0"),
        ("1.0.4", "1.0.4"),
        ("v1.0.2-rc1", "1.0.2"),
    ],
)
def test_parse_release_tag(tag: str, expected: str) -> None:
    assert parse_release_tag(tag) == expected


def test_lstrip_antipattern_demonstration() -> None:
    """Document why lstrip/replace must not be used for v1.x tags."""
    assert "v1.0.2".lstrip("v1.") == "0.2"
    assert "v1.0.2".replace("v1.", "") == "0.2"
    assert parse_release_tag("v1.0.2") == "1.0.2"


def test_invalid_tag_raises() -> None:
    with pytest.raises(ValueError, match="Not a release tag"):
        parse_release_tag("latest")
