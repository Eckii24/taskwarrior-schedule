"""Main Textual application for the schedule TUI."""

from textual.app import ComposeResult, App
from textual.binding import Binding


class ScheduleApp(App):
    """Main application class for schedule TUI."""

    TITLE = "Schedule"
    SUBTITLE = "TaskWarrior Task Rescheduler"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
    ]

    def compose(self) -> ComposeResult:
        """Compose the application UI."""
        from textual.widgets import Header, Footer

        yield Header()
        yield Footer()
