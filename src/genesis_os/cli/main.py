"""genesis-os CLI: Typer-based command-line interface.

Entry point: ``genesis-os``

Commands:
    cycle      Run the GenesisOS phase-transition loop.
    info       Display package and system information.
    phases     List available phases and their CREP focus.
    simulate   Run a headless simulation and print results as JSON.
"""

from __future__ import annotations

import json
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table

from genesis_os import __version__
from genesis_os.core.orchestrator import GenesisConfig, GenesisOS, GenesisState
from genesis_os.core.phase import Phase

app = typer.Typer(
    name="genesis-os",
    help="Self-reflecting OS framework for GenesisAeon.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=True,
)
console = Console()


def _state_table(state: GenesisState) -> Table:
    """Build a rich Table from a GenesisState."""
    table = Table(title=f"Cycle {state.cycle}", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Phase", state.phase.value)
    table.add_row("Entropy (H)", f"{state.entropy:.6f}")
    table.add_row("Φ(H)", f"{state.phi:.6f}")
    table.add_row("Lagrangian (L)", f"{state.lagrangian:.6f}")
    if state.crep:
        table.add_row("CREP C", f"{state.crep.coherence:.4f}")
        table.add_row("CREP R", f"{state.crep.resonance:.4f}")
        table.add_row("CREP E", f"{state.crep.emergence:.4f}")
        table.add_row("CREP P", f"{state.crep.poetics:.4f}")
        table.add_row("Γ (CREP coupling)", f"{state.crep.gamma:.6f}")
    table.add_row("Transitions", str(len(state.transitions)))
    return table


@app.command()
def cycle(
    entropy: Annotated[float, typer.Option("--entropy", "-e", help="Initial entropy H ∈ [0,1].")] = 0.5,
    phases: Annotated[bool, typer.Option("--phases", help="Print phase transitions.")] = False,
    simulate: Annotated[bool, typer.Option("--simulate", help="Headless mode; print JSON summary.")] = False,
    visualize: Annotated[bool, typer.Option("--visualize", help="Render Mandala dashboard.")] = False,
    sonify: Annotated[bool, typer.Option("--sonify", help="Generate sonification output.")] = False,
    max_cycles: Annotated[int, typer.Option("--max-cycles", "-n", help="Number of cycles.")] = 20,
    alpha: Annotated[float, typer.Option("--alpha", help="Self-reflection learning rate.")] = 0.1,
    seed: Annotated[int | None, typer.Option("--seed", help="Random seed.")] = None,
) -> None:
    """[bold]Run the GenesisOS phase-transition loop.[/bold]

    Example:

        genesis-os cycle --entropy 0.4 --phases --max-cycles 50
    """
    if not 0.0 <= entropy <= 1.0:
        console.print("[red]Error:[/red] entropy must be in [0.0, 1.0]")
        raise typer.Exit(code=1)

    config = GenesisConfig(
        entropy=entropy,
        alpha=alpha,
        max_cycles=max_cycles,
        seed=seed,
    )
    genesis = GenesisOS(config=config)

    if simulate:
        # Headless JSON output
        final = genesis.run()
        summary = {
            "version": __version__,
            "cycles": final.cycle,
            "final_phase": final.phase.value,
            "entropy": final.entropy,
            "phi": final.phi,
            "lagrangian": final.lagrangian,
            "transitions": len(final.transitions),
            "crep": final.crep.model_dump() if final.crep else None,
        }
        console.print_json(json.dumps(summary))
        return

    console.print(
        Panel.fit(
            f"[bold cyan]genesis-os[/bold cyan] v{__version__}\n"
            f"entropy={entropy}  α={alpha}  cycles={max_cycles}",
            title="GenesisAeon",
            border_style="magenta",
        )
    )

    last_state: GenesisState | None = None

    with Progress(SpinnerColumn(), "[progress.description]{task.description}", TimeElapsedColumn(), console=console) as progress:
        task = progress.add_task("[cyan]Running phase-transition loop...", total=max_cycles)
        for state in genesis.phase_transition_loop():
            last_state = state
            progress.advance(task)
            if phases and state.transitions:
                last_t = state.transitions[-1]
                console.log(
                    f"[yellow]⟳[/yellow] {last_t.from_phase.value} → "
                    f"[bold]{last_t.to_phase.value}[/bold]  Γ={last_t.trigger_gamma:.4f}"
                )

    if last_state is not None:
        console.print(_state_table(last_state))

    if visualize:
        _run_visualize(last_state)

    if sonify and last_state is not None:
        _run_sonify(last_state)


def _run_visualize(state: GenesisState | None) -> None:
    """Invoke Mandala dashboard rendering."""
    try:
        from genesis_os.dashboard.mandala import MandalaDashboard

        dashboard = MandalaDashboard()
        if state and state.crep:
            dashboard.render_ascii(state.crep)
    except ImportError:  # pragma: no cover
        console.print(
            "[yellow]Warning:[/yellow] mandala dashboard requires the [full-stack] extra: "
            "pip install genesis-os[full-stack]"
        )


def _run_sonify(state: GenesisState) -> None:
    """Invoke sonification output."""
    try:
        from genesis_os.dashboard.sonification import Sonifier

        sonifier = Sonifier()
        if state.crep:
            result = sonifier.crep_to_frequencies(state.crep)
            console.print(f"[magenta]Sonification frequencies:[/magenta] {result}")
    except ImportError:  # pragma: no cover
        console.print(
            "[yellow]Warning:[/yellow] sonification requires the [full-stack] extra: "
            "pip install genesis-os[full-stack]"
        )


@app.command()
def info() -> None:
    """Display package and system information."""
    table = Table(title="genesis-os info", show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Version", __version__)
    table.add_row("Python", sys.version.split()[0])
    table.add_row("Phases", ", ".join(p.value for p in Phase))

    try:
        import numpy as np

        table.add_row("NumPy", np.__version__)
    except ImportError:  # pragma: no cover
        table.add_row("NumPy", "not installed")

    console.print(table)


@app.command(name="phases")
def list_phases() -> None:
    """List available phases and their CREP focus axes."""
    table = Table(title="Phase Matrix", show_header=True, header_style="bold magenta")
    table.add_column("Phase", style="cyan")
    table.add_column("CREP Focus", style="yellow")
    table.add_column("Description", style="white")
    for phase in Phase:
        table.add_row(phase.value, phase.crep_focus, phase.description)
    console.print(table)


def main() -> None:  # pragma: no cover
    """Entry point for the genesis-os CLI."""
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
