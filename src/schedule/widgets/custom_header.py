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

    def __init__(
        self,
        filter_text: str = "",
        active_fields: str = "",
        sort_mode: str = "default",
        date_format: str = "absolute",
    ):
        super().__init__()
        self.filter_text = filter_text
        self.active_fields = active_fields
        self.sort_mode = sort_mode
        self.date_format = date_format

    def compose(self) -> ComposeResult:
        yield Static("Schedule", classes="app-title")
        yield Static(self._build_status_text(), classes="status-line")

    def _build_status_text(self) -> str:
        return (
            f"Filter: {self.filter_text}   "
            f"Active: {self.active_fields}   "
            f"Sort: {self.sort_mode}   "
            f"Date: {self.date_format}"
        )

    def update_status(
        self,
        filter_text: str,
        active_fields: str,
        sort_mode: str = "default",
        date_format: str = "absolute",
    ) -> None:
        self.filter_text = filter_text
        self.active_fields = active_fields
        self.sort_mode = sort_mode
        self.date_format = date_format

        status_line = self.query_one(".status-line", Static)
        status_line.update(self._build_status_text())
