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
        Binding("tab", "toggle_selection", "Select", show=False),
        Binding("shift+a", "select_all", "All", show=False),
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
        self.selected_tasks: set[str] = set()

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

    def action_toggle_selection(self) -> None:
        """Toggle selection of current cursor row."""
        table = self.query_one("#task-table", DataTable)
        try:
            # Get current cursor row index
            row_index = table.cursor_row
            if row_index < 0 or row_index >= len(self.tasks):
                return

            # Get task UUID from corresponding task in self.tasks
            task = self.tasks[row_index]
            task_uuid = task.get("uuid", "")

            if not task_uuid:
                return

            # Toggle UUID in selected_tasks
            if task_uuid in self.selected_tasks:
                self.selected_tasks.remove(task_uuid)
            else:
                self.selected_tasks.add(task_uuid)

            # Update visual indicator
            self._update_row_styling(row_index)
        except Exception:
            pass

    def action_select_all(self) -> None:
        """Select all visible tasks."""
        # Add all task UUIDs to selected_tasks
        for task in self.tasks:
            task_uuid = task.get("uuid", "")
            if task_uuid:
                self.selected_tasks.add(task_uuid)

        # Update visual indicators for all rows
        table = self.query_one("#task-table", DataTable)
        for row_index in range(len(self.tasks)):
            self._update_row_styling(row_index)

    def _update_row_styling(self, row_index: int) -> None:
        """Update row styling to show selection state."""
        table = self.query_one("#task-table", DataTable)
        if row_index < 0 or row_index >= len(self.tasks):
            return

        task = self.tasks[row_index]
        task_uuid = task.get("uuid", "")

        if not task_uuid:
            return

        # Get the row key
        row_key = table.get_row_at(row_index) if hasattr(table, "get_row_at") else None

        # Simple approach: add visual marker via updating cell content
        # We'll use a marker character in the first column if selected
        if task_uuid in self.selected_tasks:
            # Update first cell with selection marker
            if hasattr(table, "update_cell"):
                current_id = str(task.get("id", row_index + 1))
                table.update_cell(row_index, 0, f"● {current_id}")
        else:
            # Remove marker
            if hasattr(table, "update_cell"):
                current_id = str(task.get("id", row_index + 1))
                table.update_cell(row_index, 0, current_id)

    def action_cursor_down(self) -> None:
        """Move cursor down in the table."""
        table = self.query_one("#task-table", DataTable)
        table.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in the table."""
        table = self.query_one("#task-table", DataTable)
        table.action_cursor_up()

    def get_selected_tasks(self) -> list[str]:
        """Get list of selected task UUIDs. Returns current row if none selected."""
        if self.selected_tasks:
            return list(self.selected_tasks)

        # Return current cursor row task UUID if none selected
        try:
            table = self.query_one("#task-table", DataTable)
            row_index = table.cursor_row
            if 0 <= row_index < len(self.tasks):
                task_uuid = self.tasks[row_index].get("uuid", "")
                if task_uuid:
                    return [task_uuid]
        except Exception:
            pass

        return []

    def clear_selection(self) -> None:
        """Clear all selection and remove visual indicators."""
        # Clear selected tasks set
        self.selected_tasks.clear()

        # Remove visual indicators from all rows
        try:
            table = self.query_one("#task-table", DataTable)
            for row_index in range(len(self.tasks)):
                self._update_row_styling(row_index)
        except Exception:
            pass
