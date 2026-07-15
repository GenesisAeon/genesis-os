"""Contract tests: Diamond interface spec + migrated reference UTAC batch."""

from __future__ import annotations

import importlib
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = pytest.mark.contract

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CONTRACT_PATH = _REPO_ROOT / "contracts" / "diamond.interface.yaml"

_REFERENCE_UTACS: list[tuple[str, str, str, Callable[[], Any]]] = [
    ("amoc_utac", "AmocUTAC", "amoc-utac", lambda m: m.AmocUTAC(seed=42)),
    ("beta_clustering", "BetaClusteringUTAC", "beta-clustering-utac", lambda m: m.BetaClusteringUTAC()),
    (
        "implosive_origin",
        "ImplosiveOriginUTAC",
        "implosive-origin-utac",
        lambda m: m.ImplosiveOriginUTAC(),
    ),
    ("phi_scaling", "PhiScalingValidator", "phi-scaling-validator", lambda m: m.PhiScalingValidator()),
]


@pytest.fixture(scope="module")
def contract_spec() -> dict[str, Any]:
    assert _CONTRACT_PATH.is_file(), f"Missing {_CONTRACT_PATH}"
    data = yaml.safe_load(_CONTRACT_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_diamond_contract_file_exists():
    assert _CONTRACT_PATH.is_file()


def test_diamond_contract_required_methods(contract_spec: dict[str, Any]) -> None:
    names = {m["name"] for m in contract_spec["required_methods"]}
    assert names == {
        "run_cycle",
        "get_crep_state",
        "get_utac_state",
        "get_phase_events",
        "to_zenodo_record",
    }


def test_diamond_contract_crep_keys(contract_spec: dict[str, Any]) -> None:
    crep = next(m for m in contract_spec["required_methods"] if m["name"] == "get_crep_state")
    assert set(crep["required_keys"]) == {"C", "R", "E", "P", "Gamma"}


def test_diamond_contract_utac_keys(contract_spec: dict[str, Any]) -> None:
    utac = next(m for m in contract_spec["required_methods"] if m["name"] == "get_utac_state")
    assert set(utac["required_keys"]) == {"H", "H_star", "K_eff"}


def test_diamond_contract_ci_packages_match_batch(contract_spec: dict[str, Any]) -> None:
    ci = contract_spec.get("ci_reference_packages", [])
    ci_classes = {(e["import"], e["class"]) for e in ci}
    batch_classes = {(mod, cls) for mod, cls, _, _ in _REFERENCE_UTACS}
    assert batch_classes <= ci_classes


@pytest.mark.parametrize(
    ("module_name", "class_name", "pip_name"),
    [(mod, cls, pip) for mod, cls, pip, _ in _REFERENCE_UTACS],
)
def test_reference_utac_validate_diamond_instance(
    module_name: str,
    class_name: str,
    pip_name: str,
) -> None:
    pytest.importorskip("diamond_setup")
    mod = pytest.importorskip(module_name)
    factory = next(f for m, c, _, f in _REFERENCE_UTACS if m == module_name and c == class_name)
    from diamond_setup.validation import validate_diamond_instance

    instance = factory(mod)
    errors = validate_diamond_instance(instance)
    assert errors == [], f"{pip_name}: {errors}"
