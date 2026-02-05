"""Main Textual application for the schedule TUI."""

from textual.app import ComposeResult, App
from textual.binding import Binding
from textual.widgets import Header, Footer, DataTable, Static
from textual.notifications import Notification

from schedule.config import load_config, DateFieldManager
from schedule.taskwarrior import TaskWarriorClient
from schedule.widgets.report_modal import ReportModal


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
        # Hotkey scheduling bindings
        Binding("0", "clear_date", "Clear", show=False),
        Binding("1", "schedule_1", "1", show=False),
        Binding("2", "schedule_2", "2", show=False),
        Binding("3", "schedule_3", "3", show=False),
        Binding("4", "schedule_4", "4", show=False),
        Binding("5", "schedule_5", "5", show=False),
        Binding("6", "schedule_6", "6", show=False),
        Binding("7", "schedule_7", "7", show=False),
        Binding("8", "schedule_8", "8", show=False),
        Binding("9", "schedule_9", "9", show=False),
        # Date field toggles
        Binding("w", "toggle_wait", "Wait", show=False),
        Binding("s", "toggle_scheduled", "Scheduled", show=False),
        Binding("d", "toggle_due", "Due", show=False),
        # Report modal
        Binding("r", "change_report", "Report", show=False),
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

    def _update_info_bar(self) -> None:
        """Update info bar to show active date fields."""
        try:
            info_bar = self.query_one("#info-bar", Static)
            active_fields = self.date_field_mgr.get_active()
            info_bar.update(
                f"Report: {self.current_report} | Active: {', '.join(active_fields) if active_fields else 'None'}"
            )
        except Exception:
            pass

    def refresh_tasks(self) -> None:
        """Reload tasks from TaskWarrior and repopulate the table."""
        try:
            table = self.query_one("#task-table", DataTable)

            # Load fresh tasks from TaskWarrior
            self.tasks = self.tw_client.get_tasks(self.current_report)

            # Clear the table
            table.clear()

            # Re-add columns
            table.add_columns(
                "ID", "Description", "Project", "Scheduled", "Due", "Wait"
            )

            # Repopulate rows
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
                table.add_row("", "No tasks", "", "", "", "")
        except Exception as e:
            self.notify(f"Error refreshing tasks: {str(e)}", severity="error")

    def _show_error(self, message: str) -> None:
        """Show error notification to user."""
        try:
            self.notify(message, severity="error")
        except Exception:
            pass

    def action_toggle_wait(self) -> None:
        """Toggle 'wait' date field."""
        self.date_field_mgr.toggle("wait")
        self._update_info_bar()

    def action_toggle_scheduled(self) -> None:
        """Toggle 'scheduled' date field."""
        self.date_field_mgr.toggle("scheduled")
        self._update_info_bar()

    def action_toggle_due(self) -> None:
        """Toggle 'due' date field."""
        self.date_field_mgr.toggle("due")
        self._update_info_bar()

    def action_clear_date(self) -> None:
        """Clear date fields (hotkey 0) on selected tasks."""
        if not self.date_field_mgr.get_active():
            self._show_error("No active date fields to clear")
            return

        selected_uuids = self.get_selected_tasks()
        if not selected_uuids:
            self._show_error("No tasks selected")
            return

        # Batch modify all selected tasks
        for uuid in selected_uuids:
            for field in self.date_field_mgr.get_active():
                success = self.tw_client.modify_task(uuid, **{field: ""})
                if not success:
                    self._show_error(f"Failed to clear {field} for task {uuid}")

        # Clear selection and refresh
        self.clear_selection()
        self.refresh_tasks()

    def action_schedule_1(self) -> None:
        """Schedule tasks using hotkey 1."""
        self._schedule_with_hotkey("1")

    def action_schedule_2(self) -> None:
        """Schedule tasks using hotkey 2."""
        self._schedule_with_hotkey("2")

    def action_schedule_3(self) -> None:
        """Schedule tasks using hotkey 3."""
        self._schedule_with_hotkey("3")

    def action_schedule_4(self) -> None:
        """Schedule tasks using hotkey 4."""
        self._schedule_with_hotkey("4")

    def action_schedule_5(self) -> None:
        """Schedule tasks using hotkey 5."""
        self._schedule_with_hotkey("5")

    def action_schedule_6(self) -> None:
        """Schedule tasks using hotkey 6."""
        self._schedule_with_hotkey("6")

    def action_schedule_7(self) -> None:
        """Schedule tasks using hotkey 7."""
        self._schedule_with_hotkey("7")

    def action_schedule_8(self) -> None:
        """Schedule tasks using hotkey 8."""
        self._schedule_with_hotkey("8")

    def action_schedule_9(self) -> None:
        """Schedule tasks using hotkey 9."""
        self._schedule_with_hotkey("9")

    def _schedule_with_hotkey(self, hotkey: str) -> None:
        """Schedule selected tasks using a hotkey value."""
        # Check if hotkey has a configured value
        if hotkey not in self.config.get("hotkeys", {}):
            self._show_error(f"Hotkey {hotkey} not configured")
            return

        hotkey_value = self.config["hotkeys"][hotkey]

        # Check if there are active date fields
        active_fields = self.date_field_mgr.get_active()
        if not active_fields:
            self._show_error("No active date fields. Use W/S/D to toggle.")
            return

        # Get selected tasks
        selected_uuids = self.get_selected_tasks()
        if not selected_uuids:
            self._show_error("No tasks selected")
            return

        # Batch modify all selected tasks for all active fields
        for uuid in selected_uuids:
            modifications = {}
            for field in active_fields:
                modifications[field] = hotkey_value

            success = self.tw_client.modify_task(uuid, **modifications)
            if not success:
                self._show_error(f"Failed to schedule task {uuid}")

        # Clear selection and refresh
        self.clear_selection()
        self.refresh_tasks()

    def action_change_report(self) -> None:
        """Open modal to change current report (hotkey R)."""

        def on_report_result(result: str | None) -> None:
            """Handle modal result."""
            if result is not None:
                # Update current report
                self.current_report = result
                # Update info bar
                self._update_info_bar()
                # Reload tasks with new report
                self.refresh_tasks()

        self.push_screen(ReportModal(), callback=on_report_result)
