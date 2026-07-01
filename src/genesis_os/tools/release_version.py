"""Safe release-tag → semver parsing for PyPI/Zenodo/GitHub."""

from __future__ import annotations

import re

_SEMVER_RE = re.compile(
    r"^v?(?P<version>\d+\.\d+\.\d+)(?:-(?P<suffix>rc\d+|alpha\d+|beta\d+))?$"
)


def parse_release_tag(tag: str) -> str:
    """Parse ``v1.0.2`` / ``1.0.2`` → ``1.0.2``.

    Never use ``str.lstrip('v1.')`` or ``tag.replace('v1.', '')`` — those turn
    ``v1.0.2`` into ``0.2`` (the leading major ``1`` is swallowed).
    """
    normalized = tag.strip()
    match = _SEMVER_RE.match(normalized)
    if not match:
        msg = f"Not a release tag: {tag!r} (expected vX.Y.Z or X.Y.Z)"
        raise ValueError(msg)
    return match.group("version")