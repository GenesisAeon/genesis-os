"""Unit tests for genesis_os.cli.main."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from genesis_os import __version__
from genesis_os.cli.main import app

runner = CliRunner()


class TestCLICycle:
    def test_cycle_default(self) -> None:
        result = runner.invoke(app, ["cycle", "--max-cycles", "3"])
        assert result.exit_code == 0

    def test_cycle_with_entropy(self) -> None:
        result = runner.invoke(app, ["cycle", "--entropy", "0.3", "--max-cycles", "3"])
        assert result.exit_code == 0

    def test_cycle_simulate_json_output(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "3"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "version" in data
        assert "cycles" in data

    def test_cycle_simulate_version_correct(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "2"])
        data = json.loads(result.output)
        assert data["version"] == __version__

    def test_cycle_simulate_entropy_in_output(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "2"])
        data = json.loads(result.output)
        assert "entropy" in data
        assert 0.0 <= data["entropy"] <= 1.0

    def test_cycle_simulate_transitions_key(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "5"])
        data = json.loads(result.output)
        assert "transitions" in data

    def test_cycle_invalid_entropy(self) -> None:
        result = runner.invoke(app, ["cycle", "--entropy", "1.5"])
        assert result.exit_code != 0

    def test_cycle_invalid_entropy_negative(self) -> None:
        result = runner.invoke(app, ["cycle", "--entropy", "-0.1"])
        assert result.exit_code != 0

    def test_cycle_phases_flag(self) -> None:
        result = runner.invoke(app, ["cycle", "--phases", "--max-cycles", "3"])
        assert result.exit_code == 0

    def test_cycle_with_seed(self) -> None:
        result = runner.invoke(app, ["cycle", "--seed", "42", "--max-cycles", "3"])
        assert result.exit_code == 0

    def test_cycle_with_alpha(self) -> None:
        result = runner.invoke(app, ["cycle", "--alpha", "0.2", "--max-cycles", "3"])
        assert result.exit_code == 0

    def test_cycle_simulate_crep_not_none(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "5"])
        data = json.loads(result.output)
        assert data["crep"] is not None

    def test_cycle_simulate_final_phase_present(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "3"])
        data = json.loads(result.output)
        assert "final_phase" in data

    def test_cycle_simulate_phi_present(self) -> None:
        result = runner.invoke(app, ["cycle", "--simulate", "--max-cycles", "3"])
        data = json.loads(result.output)
        assert "phi" in data
        assert data["phi"] > 0.0


class TestCLIInfo:
    def test_info_runs(self) -> None:
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0

    def test_info_contains_version(self) -> None:
        result = runner.invoke(app, ["info"])
        assert __version__ in result.output


class TestCLIPhases:
    def test_phases_runs(self) -> None:
        result = runner.invoke(app, ["phases"])
        assert result.exit_code == 0

    def test_phases_contains_initiation(self) -> None:
        result = runner.invoke(app, ["phases"])
        assert "Initiation" in result.output

    def test_phases_contains_activation(self) -> None:
        result = runner.invoke(app, ["phases"])
        assert "Activation" in result.output

    def test_phases_contains_integration(self) -> None:
        result = runner.invoke(app, ["phases"])
        assert "Integration" in result.output

    def test_phases_contains_reflection(self) -> None:
        result = runner.invoke(app, ["phases"])
        assert "Reflection" in result.output

    def test_phases_contains_crep_focus(self) -> None:
        result = runner.invoke(app, ["phases"])
        for focus in ["C", "R", "E", "P"]:
            assert focus in result.output
