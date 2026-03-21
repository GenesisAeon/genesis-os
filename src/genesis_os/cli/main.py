"""genesis-os CLI: Typer-based command-line interface.

Entry point: ``genesis-os``

Commands:
    cycle      Run the GenesisOS phase-transition loop.
    info       Display package and system information.
    phases     List available phases and their CREP focus.

Use ``--simulate`` for headless JSON output, ``--gui`` to launch the Dash
web dashboard (requires ``pip install genesis-os[gui]``).
"""

from __future__ import annotations

import json
import sys
from typing import Annotated, Any

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
    table.add_row("Emergence Events", str(len(state.emergence_events)))
    esummary = state.metadata.get("emergence_summary", {})
    if esummary:
        table.add_row("Active Nodes", str(esummary.get("active_nodes", 0)))
        table.add_row("Node Density", f"{esummary.get('mean_density', 0.0):.4f}")
    return table


@app.command()
def cycle(
    entropy: Annotated[float, typer.Option("--entropy", "-e", help="Initial entropy H ∈ [0,1].")] = 0.5,
    phases: Annotated[bool, typer.Option("--phases", help="Print phase transitions.")] = False,
    simulate: Annotated[bool, typer.Option("--simulate", help="Headless mode; print JSON summary.")] = False,
    visualize: Annotated[bool, typer.Option("--visualize", help="Render Mandala dashboard.")] = False,
    sonify: Annotated[bool, typer.Option("--sonify", help="Generate sonification output.")] = False,
    gui: Annotated[bool, typer.Option("--gui", help="Launch live Dash web GUI (requires genesis-os[gui]).")] = False,
    gui_port: Annotated[int, typer.Option("--gui-port", help="Dash server port.")] = 8050,
    gui_host: Annotated[str, typer.Option("--gui-host", help="Dash server host.")] = "127.0.0.1",
    max_cycles: Annotated[int, typer.Option("--max-cycles", "-n", help="Number of cycles.")] = 20,
    alpha: Annotated[float, typer.Option("--alpha", help="Self-reflection learning rate.")] = 0.1,
    seed: Annotated[int | None, typer.Option("--seed", help="Random seed.")] = None,
) -> None:
    """[bold]Run the GenesisOS phase-transition loop.[/bold]

    Example:

        genesis-os cycle --entropy 0.4 --phases --max-cycles 50 --gui
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
            "emergence_events": len(final.emergence_events),
            "crep": final.crep.model_dump() if final.crep else None,
            "emergence_summary": final.metadata.get("emergence_summary", {}),
        }
        console.print_json(json.dumps(summary))
        return

    # Optional: launch GUI in background thread before the loop starts
    web_gui = None
    if gui:
        web_gui = _start_gui(gui_host, gui_port)

    console.print(
        Panel.fit(
            f"[bold cyan]genesis-os[/bold cyan] v{__version__}\n"
            f"entropy={entropy}  α={alpha}  cycles={max_cycles}"
            + (f"  gui=http://{gui_host}:{gui_port}" if gui and web_gui else ""),
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
            if phases and state.emergence_events:
                last_e = state.emergence_events[-1]
                console.log(
                    f"[green]✦[/green] Emergence event: nodes={last_e.node_count} "
                    f"rate={last_e.emergence_rate:.4f}"
                )
            if web_gui is not None:
                _push_gui_snapshot(web_gui, state)

    if last_state is not None:
        console.print(_state_table(last_state))

    if visualize:
        _run_visualize(last_state)

    if sonify and last_state is not None:
        _run_sonify(last_state)


def _start_gui(host: str, port: int) -> Any | None:
    """Launch the Dash GUI in a daemon thread and return the GenesisWebGUI instance."""
    import threading

    try:
        from genesis_os.dashboard.web_gui import GenesisWebGUI

        web_gui: Any = GenesisWebGUI()
        web_gui.build_app()

        def _serve() -> None:
            import contextlib
            import logging

            logging.getLogger("werkzeug").setLevel(logging.ERROR)
            logging.getLogger("dash").setLevel(logging.ERROR)
            with contextlib.suppress(Exception, SystemExit):  # pragma: no cover
                web_gui.run(host=host, port=port, debug=False)

        t = threading.Thread(target=_serve, daemon=True)
        t.start()
        console.print(f"[green]GUI started:[/green] http://{host}:{port}")
        return web_gui
    except ImportError:  # pragma: no cover
        console.print(
            "[yellow]Warning:[/yellow] Dash not installed. "
            "Run: pip install genesis-os[gui]"
        )
        return None
    except Exception as exc:  # pragma: no cover
        console.print(f"[yellow]Warning:[/yellow] GUI failed to start: {exc}")
        return None


def _push_gui_snapshot(web_gui: Any, state: GenesisState) -> None:
    """Push a GenesisState snapshot into the GUI queue."""
    try:
        from genesis_os.dashboard.web_gui import GUISnapshot

        esummary = state.metadata.get("emergence_summary", {})
        snap = GUISnapshot(
            cycle=state.cycle,
            phase=state.phase.value,
            entropy=state.entropy,
            phi=state.phi,
            lagrangian=state.lagrangian,
            gamma=state.crep.gamma if state.crep else 0.0,
            coherence=state.crep.coherence if state.crep else 0.5,
            resonance=state.crep.resonance if state.crep else 0.5,
            emergence=state.crep.emergence if state.crep else 0.5,
            poetics=state.crep.poetics if state.crep else 0.5,
            mean_density=float(esummary.get("mean_density", 0.0)),
            active_nodes=int(esummary.get("active_nodes", 0)),
            emergence_events=len(state.emergence_events),
            phase_transition=bool(
                state.transitions and state.transitions[-1].cycle == state.cycle
            ),
        )
        web_gui.push_snapshot(snap)
    except Exception:  # pragma: no cover
        pass


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
