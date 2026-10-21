"""Execute all dashboard page functions with a lightweight Streamlit stand-in.

This exercises data access, chart construction and empty-filter branches without
claiming a real web-browser render; Streamlit itself is installed in GitHub CI.
"""
from pathlib import Path
import runpy
import sys
import types
import plotly.graph_objects as go
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


class _MockUI:
    def __init__(self, empty_filters=False):
        self.empty_filters = empty_filters
        self.visited = []
        self.charts = 0
        self.tables = 0
        self.sidebar = self

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def __getattr__(self, key):
        if key == "cache_data":
            return lambda **_kwargs: lambda fn: fn
        if key == "navigation":
            return lambda pages: _MockNavigation(self, pages)
        if key == "Page":
            return lambda func, **_kwargs: func
        if key == "columns":
            return lambda widths: [self] * (widths if isinstance(widths, int) else len(widths))
        if key in ("expander", "container"):
            return lambda *_args, **_kwargs: self
        if key in ("radio", "selectbox"):
            return lambda _label, options, **_kwargs: list(options)[0]
        if key == "multiselect":
            return lambda _label, options, default, **_kwargs: [] if self.empty_filters else default
        if key == "slider":
            return lambda _label, min_value, max_value, value, **_kwargs: value
        if key == "plotly_chart":
            def capture(fig, **_kwargs):
                assert isinstance(fig, go.Figure)
                assert fig.to_json()  # Fully serializable Plotly traces/layout.
                self.charts += 1
            return capture
        if key == "dataframe":
            def capture(frame, **_kwargs):
                assert isinstance(frame, pd.DataFrame)
                self.tables += 1
            return capture
        if key == "stop":
            return lambda: (_ for _ in ()).throw(RuntimeError("Streamlit app stopped unexpectedly"))
        return lambda *_args, **_kwargs: None


class _MockNavigation:
    def __init__(self, mock, pages):
        self.mock, self.pages = mock, pages

    def run(self):
        for callback in self.pages:
            self.mock.visited.append(callback.__name__)
            callback()


def run_fake_ui(monkeypatch, empty_filters):
    stub = _MockUI(empty_filters=empty_filters)
    module = types.ModuleType("streamlit")
    module.__getattr__ = stub.__getattr__
    module.sidebar = stub
    monkeypatch.setitem(sys.modules, "streamlit", module)
    runpy.run_path(str(ROOT / "streamlit_app.py"), run_name="__main__")
    assert stub.visited == [
        "overview", "products", "customers", "recommendations", "quality",
        "sql_explorer", "methodology",
    ]
    assert stub.tables >= 4
    return stub


def test_each_streamlit_view_builds_figures_and_tables(monkeypatch):
    dashboard = run_fake_ui(monkeypatch, empty_filters=False)
    assert dashboard.charts >= 8


def test_each_streamlit_view_handles_empty_selection(monkeypatch):
    dashboard = run_fake_ui(monkeypatch, empty_filters=True)
    assert dashboard.charts >= 2
