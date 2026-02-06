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
        sort_direction: str = "",
    ):
        super().__init__()
        self.filter_text = filter_text
        self.active_fields = active_fields
        self.sort_mode = sort_mode
        self.date_format = date_format
        self.sort_direction = sort_direction

    def compose(self) -> ComposeResult:
        yield Static("Schedule", classes="app-title")
        yield Static(self._build_status_text(), classes="status-line")

    def _build_status_text(self) -> str:
        sort_display = self.sort_mode
        if self.sort_direction:
            sort_display += f" {self.sort_direction}"
        return (
            f"Filter: {self.filter_text}   "
            f"Active: {self.active_fields}   "
            f"Sort: {sort_display}   "
            f"Date: {self.date_format}"
        )

    def update_status(
        self,
        filter_text: str,
        active_fields: str,
        sort_mode: str = "default",
        date_format: str = "absolute",
        sort_direction: str = "",
    ) -> None:
        self.filter_text = filter_text
        self.active_fields = active_fields
        self.sort_mode = sort_mode
        self.date_format = date_format
        self.sort_direction = sort_direction

        status_line = self.query_one(".status-line", Static)
        status_line.update(self._build_status_text())
