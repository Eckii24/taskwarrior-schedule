"""Custom header widget for Schedule TUI."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Container


class CustomHeader(Container):
    DEFAULT_CSS = """
    CustomHeader {
        dock: top;
        height: auto;
        background: $panel;
        border: heavy $primary;
        padding: 0 2;
        layout: vertical;
    }

    CustomHeader .app-title {
        text-style: bold;
        height: 1;
        text-align: center;
    }

    CustomHeader .status-line {
        height: 1;
        text-align: center;
    }
    """

    def __init__(self, filter_text: str = "", active_fields: str = ""):
        super().__init__()
        self.filter_text = filter_text
        self.active_fields = active_fields

    def compose(self) -> ComposeResult:
        yield Static("Schedule", classes="app-title")
        status_text = f"Filter: {self.filter_text}   Active: {self.active_fields}"
        yield Static(status_text, classes="status-line")

    def update_status(self, filter_text: str, active_fields: str) -> None:
        self.filter_text = filter_text
        self.active_fields = active_fields

        status_line = self.query_one(".status-line", Static)
        status_line.update(f"Filter: {filter_text}   Active: {active_fields}")
