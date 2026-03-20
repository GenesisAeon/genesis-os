"""Dash-based web GUI for live GenesisOS phase-transition visualisation.

Provides :class:`GenesisWebGUI`, a self-contained Dash application that
renders the Mandala dashboard, climate-coupling indicators, and real-time
emergence event charts.  The GUI receives live state updates from the
orchestrator's ``phase_transition_loop`` via a thread-safe queue and
refreshes every ``interval_ms`` milliseconds.

Install the optional ``[gui]`` extra to use this module::

    pip install genesis-os[gui]

The GUI can be launched from the CLI::

    genesis-os cycle --gui --entropy 0.4 --max-cycles 200
"""

from __future__ import annotations

import logging
import queue
import threading
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional Dash imports – degrade gracefully if not installed
# ---------------------------------------------------------------------------
try:  # pragma: no cover
    import dash  # type: ignore[import-not-found]
    import dash_bootstrap_components as dbc  # type: ignore[import-not-found]
    import plotly.graph_objects as go  # type: ignore[import-not-found]
    from dash import Input, Output, dcc, html  # type: ignore[import-not-found]

    _DASH_AVAILABLE = True
except ImportError:
    _DASH_AVAILABLE = False
    dash = None  # type: ignore[assignment]
    dbc = None  # type: ignore[assignment]
    go = None  # type: ignore[assignment]
    dcc = None  # type: ignore[assignment]
    html = None  # type: ignore[assignment]
    Input = None  # type: ignore[assignment]
    Output = None  # type: ignore[assignment]


@dataclass
class GUISnapshot:
    """Lightweight state snapshot for the web GUI.

    Attributes:
        cycle: Orchestrator cycle index.
        phase: Active phase name.
        entropy: Current entropy H.
        phi: Self-reflection potential Φ(H).
        lagrangian: Unified Lagrangian L.
        gamma: CREP coupling Γ.
        coherence: CREP coherence C.
        resonance: CREP resonance R.
        emergence: CREP emergence E.
        poetics: CREP poetics P.
        mean_density: Mean cosmic-web node density.
        active_nodes: Number of active emergence nodes.
        emergence_events: Cumulative emergence event count.
        phase_transition: Whether a transition just occurred.
    """

    cycle: int = 0
    phase: str = "Initiation"
    entropy: float = 0.5
    phi: float = 1.0
    lagrangian: float = 0.0
    gamma: float = 0.0
    coherence: float = 0.5
    resonance: float = 0.5
    emergence: float = 0.5
    poetics: float = 0.5
    mean_density: float = 0.0
    active_nodes: int = 0
    emergence_events: int = 0
    phase_transition: bool = False


@dataclass
class GenesisWebGUI:
    """Live Dash web GUI for the GenesisOS framework.

    Extends the Mandala dashboard and climate-dashboard with real-time
    Plotly charts for CREP evolution, emergence events, and node density.

    Args:
        title: Application title shown in the browser.
        interval_ms: Refresh interval in milliseconds (default 1000).
        history_len: Number of historical data points to display (default 200).
        theme: Dash Bootstrap Components theme (default DARKLY).
    """

    title: str = "GenesisOS v0.2.0 — Live Emergence Dashboard"
    interval_ms: int = 1_000
    history_len: int = 200
    theme: str = "DARKLY"

    _app: Any = field(default=None, init=False, repr=False)
    _queue: queue.Queue[GUISnapshot] = field(
        default_factory=queue.Queue, init=False, repr=False
    )
    _history: list[GUISnapshot] = field(default_factory=list, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _running: bool = field(default=False, init=False, repr=False)

    def push_snapshot(self, snapshot: GUISnapshot) -> None:
        """Push a new state snapshot into the GUI queue.

        Thread-safe: can be called from the orchestrator thread.

        Args:
            snapshot: State snapshot to enqueue.
        """
        self._queue.put_nowait(snapshot)

    def _drain_queue(self) -> None:
        """Drain all pending snapshots into the history buffer."""
        while True:
            try:
                snap = self._queue.get_nowait()
                with self._lock:
                    self._history.append(snap)
                    if len(self._history) > self.history_len:
                        self._history.pop(0)
            except queue.Empty:
                break

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _crep_radar_figure(self, snap: GUISnapshot) -> Any:
        """Build a Plotly polar/radar chart for the CREP score."""
        if go is None:  # pragma: no cover
            return {}
        categories = ["C", "R", "E", "P", "C"]
        values = [snap.coherence, snap.resonance, snap.emergence, snap.poetics, snap.coherence]
        fig = go.Figure(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                name="CREP",
                line_color="#9b59b6",
                fillcolor="rgba(155,89,182,0.25)",
            )
        )
        fig.update_layout(
            polar={"radialaxis": {"visible": True, "range": [0, 1]}},
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#ecf0f1"},
            margin={"l": 20, "r": 20, "t": 40, "b": 20},
            title={"text": f"CREP Γ={snap.gamma:.4f}", "x": 0.5},
        )
        return fig

    def _entropy_lagrangian_figure(self, history: list[GUISnapshot]) -> Any:
        """Build an H(t) and L(t) dual-axis line chart."""
        if go is None:  # pragma: no cover
            return {}
        cycles = [s.cycle for s in history]
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=cycles,
                y=[s.entropy for s in history],
                name="Entropy H",
                line={"color": "#3498db"},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=cycles,
                y=[s.lagrangian for s in history],
                name="Lagrangian L",
                line={"color": "#e74c3c", "dash": "dot"},
                yaxis="y2",
            )
        )
        fig.update_layout(
            xaxis={"title": "Cycle"},
            yaxis={"title": "H", "range": [0, 1], "color": "#3498db"},
            yaxis2={
                "title": "L",
                "overlaying": "y",
                "side": "right",
                "color": "#e74c3c",
            },
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(18,18,18,0.8)",
            font={"color": "#ecf0f1"},
            legend={"orientation": "h", "y": 1.05},
            margin={"l": 40, "r": 60, "t": 10, "b": 40},
        )
        # Mark phase transitions
        for snap in history:
            if snap.phase_transition:
                fig.add_vline(
                    x=snap.cycle,
                    line_dash="dash",
                    line_color="#f39c12",
                    opacity=0.6,
                )
        return fig

    def _emergence_figure(self, history: list[GUISnapshot]) -> Any:
        """Build the emergence event rate and node-density chart."""
        if go is None:  # pragma: no cover
            return {}
        cycles = [s.cycle for s in history]
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=cycles,
                y=[s.emergence_events for s in history],
                name="Emergence Events",
                marker_color="#2ecc71",
                opacity=0.7,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=cycles,
                y=[s.mean_density for s in history],
                name="Node Density",
                line={"color": "#1abc9c"},
                yaxis="y2",
            )
        )
        fig.update_layout(
            xaxis={"title": "Cycle"},
            yaxis={"title": "Events", "color": "#2ecc71"},
            yaxis2={
                "title": "Density",
                "overlaying": "y",
                "side": "right",
                "range": [0, 1],
                "color": "#1abc9c",
            },
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(18,18,18,0.8)",
            font={"color": "#ecf0f1"},
            legend={"orientation": "h", "y": 1.05},
            margin={"l": 40, "r": 60, "t": 10, "b": 40},
        )
        return fig

    def _status_cards(self, snap: GUISnapshot) -> list[Any]:
        """Build a row of status metric cards."""
        if dbc is None or html is None:  # pragma: no cover
            return []
        metrics = [
            ("Phase", snap.phase, "#9b59b6"),
            ("Cycle", str(snap.cycle), "#3498db"),
            ("Entropy H", f"{snap.entropy:.4f}", "#e67e22"),
            ("Φ(H)", f"{snap.phi:.4f}", "#f39c12"),
            ("Active Nodes", str(snap.active_nodes), "#2ecc71"),
            ("Emergence ∑", str(snap.emergence_events), "#1abc9c"),
        ]
        cards = []
        for label, value, color in metrics:
            cards.append(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H6(label, className="card-title", style={"color": "#aaa"}),
                                html.H4(value, className="card-text", style={"color": color}),
                            ]
                        ),
                        style={"backgroundColor": "#1a1a2e", "border": f"1px solid {color}"},
                    ),
                    width=2,
                )
            )
        return cards

    # ------------------------------------------------------------------
    # App construction
    # ------------------------------------------------------------------

    def build_app(self) -> Any:
        """Construct and configure the Dash application.

        Returns:
            Configured ``dash.Dash`` instance, or ``None`` if Dash is not
            installed.
        """
        if not _DASH_AVAILABLE or dash is None:  # pragma: no cover
            logger.warning(
                "Dash not installed. Install genesis-os[gui] to use the web GUI."
            )
            return None

        theme_url = getattr(dbc.themes, self.theme, dbc.themes.DARKLY)
        app = dash.Dash(
            __name__,
            external_stylesheets=[theme_url],
            title=self.title,
        )

        app.layout = html.Div(
            [
                dcc.Interval(id="interval", interval=self.interval_ms, n_intervals=0),
                html.H2(
                    self.title,
                    style={"textAlign": "center", "color": "#9b59b6", "padding": "1rem"},
                ),
                # Status cards row – updated via callback
                dbc.Container(
                    dbc.Row(id="status-cards", className="mb-3"),
                    fluid=True,
                ),
                # Main charts
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Graph(
                                        id="crep-radar",
                                        style={"height": "350px"},
                                        config={"displayModeBar": False},
                                    ),
                                    width=4,
                                ),
                                dbc.Col(
                                    dcc.Graph(
                                        id="entropy-chart",
                                        style={"height": "350px"},
                                        config={"displayModeBar": False},
                                    ),
                                    width=8,
                                ),
                            ],
                            className="mb-3",
                        ),
                        dbc.Row(
                            dbc.Col(
                                dcc.Graph(
                                    id="emergence-chart",
                                    style={"height": "300px"},
                                    config={"displayModeBar": False},
                                ),
                                width=12,
                            ),
                        ),
                    ],
                    fluid=True,
                ),
            ],
            style={"backgroundColor": "#0d0d1a", "minHeight": "100vh"},
        )

        self._register_callbacks(app)
        self._app = app
        return app

    def _register_callbacks(self, app: Any) -> None:
        """Register all Dash callbacks for live update."""
        if not _DASH_AVAILABLE:  # pragma: no cover
            return

        @app.callback(  # type: ignore[misc]
            [
                Output("status-cards", "children"),
                Output("crep-radar", "figure"),
                Output("entropy-chart", "figure"),
                Output("emergence-chart", "figure"),
            ],
            Input("interval", "n_intervals"),
        )
        def update_all(_n: int) -> tuple[list[Any], Any, Any, Any]:  # pragma: no cover
            self._drain_queue()
            with self._lock:
                history = list(self._history)

            snap = history[-1] if history else GUISnapshot()
            cards = self._status_cards(snap)
            radar = self._crep_radar_figure(snap)
            entropy_chart = self._entropy_lagrangian_figure(history)
            emergence_chart = self._emergence_figure(history)
            return cards, radar, entropy_chart, emergence_chart

    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 8050,
        debug: bool = False,
    ) -> None:
        """Start the Dash development server (blocking).

        Args:
            host: Network host to bind (default ``'127.0.0.1'``).
            port: TCP port to listen on (default ``8050``).
            debug: Enable Dash debug mode (default ``False``).

        Raises:
            RuntimeError: If Dash is not installed.
        """
        if not _DASH_AVAILABLE:  # pragma: no cover
            msg = "Dash not installed. Run: pip install genesis-os[gui]"
            raise RuntimeError(msg)

        if self._app is None:
            self.build_app()

        logger.info("Starting GenesisOS Web GUI at http://%s:%d", host, port)
        self._running = True
        self._app.run(host=host, port=port, debug=debug)

    @property
    def is_available(self) -> bool:
        """Return True if the [gui] extra (Dash) is installed."""
        return _DASH_AVAILABLE
