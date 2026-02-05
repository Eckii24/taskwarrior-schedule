"""Main Textual application for the schedule TUI."""

from textual.app import ComposeResult, App
from textual.binding import Binding
from textual.widgets import Header, Footer, DataTable, Static

from schedule.config import load_config, DateFieldManager
from schedule.taskwarrior import TaskWarriorClient


class ScheduleApp(App):
    """Main application class for schedule TUI."""

    TITLE = "Schedule"
    SUBTITLE = "TaskWarrior Task Rescheduler"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.config = load_config()
        self.tw_client = TaskWarriorClient()
        self.date_field_mgr = DateFieldManager(
            self.config.get("default_date_fields", ["scheduled"])
        )
        self.current_report = self.config.get("default_report", "next")
        self.tasks = []

    def compose(self) -> ComposeResult:
        """Compose the application UI."""
        yield Header()
        yield Static(
            f"Report: {self.current_report} | Active: {', '.join(self.date_field_mgr.get_active())}",
            id="info-bar",
        )
        yield DataTable(id="task-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        """Load and display tasks when app starts."""
        table = self.query_one("#task-table", DataTable)

        # Add columns
        table.add_columns("ID", "Description", "Project", "Scheduled", "Due", "Wait")

        try:
            # Load tasks from TaskWarrior
            self.tasks = self.tw_client.get_tasks(self.current_report)

            # Populate rows
            if self.tasks:
                for idx, task in enumerate(self.tasks, 1):
                    row_data = [
                        str(task.get("id", idx)),
                        task.get("description", "")[:50],
                        task.get("project", ""),
                        task.get("scheduled", "-"),
                        task.get("due", "-"),
                        task.get("wait", "-"),
                    ]
                    table.add_row(*row_data)
            else:
                # Show placeholder for empty list
                table.add_row("", "No tasks", "", "", "", "")
        except Exception as e:
            # Show error in table
            table.add_row("", f"Error: {str(e)}", "", "", "", "")

    def action_cursor_down(self) -> None:
        """Move cursor down in the table."""
        table = self.query_one("#task-table", DataTable)
        table.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in the table."""
        table = self.query_one("#task-table", DataTable)
        table.action_cursor_up()
