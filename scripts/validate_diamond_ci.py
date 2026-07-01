#!/usr/bin/env python3
"""CI entrypoint: validate Diamond-interface compliance for reference UTACs."""

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CONTRACT_PATH = _REPO_ROOT / "contracts" / "diamond.interface.yaml"


def _load_contract() -> dict[str, Any]:
    if not _CONTRACT_PATH.is_file():
        msg = f"Missing contract spec: {_CONTRACT_PATH}"
        raise SystemExit(msg)
    data = yaml.safe_load(_CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("diamond.interface.yaml must parse to a mapping")
    return data


def _factory_for(module_name: str, class_name: str) -> Callable[[], Any]:
    mod = importlib.import_module(module_name)
    cls = getattr(mod, class_name)
    if module_name == "amoc_utac" and class_name == "AmocUTAC":
        return lambda: cls(seed=42)
    return cls


def main() -> int:
    from diamond_setup.validation import validate_diamond_instance

    contract = _load_contract()
    packages = contract.get("ci_reference_packages", [])
    if not packages:
        print("No ci_reference_packages in contract — nothing to validate.")
        return 0

    failures: list[str] = []
    for entry in packages:
        pip_name = entry["pip"]
        module_name = entry["import"]
        class_name = entry["class"]
        label = f"{pip_name} ({module_name}.{class_name})"
        try:
            instance = _factory_for(module_name, class_name)()
            errors = validate_diamond_instance(instance)
        except Exception as exc:
            failures.append(f"{label}: {exc}")
            continue
        if errors:
            failures.append(f"{label}: " + "; ".join(errors))
        else:
            print(f"OK  {label}")

    if failures:
        print("\nDiamond validation failures:", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1

    print(f"\nAll {len(packages)} reference UTACs passed Diamond validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())