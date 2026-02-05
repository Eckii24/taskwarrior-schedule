"""Main Textual application for the schedule TUI."""

from textual.app import ComposeResult, App
from textual.binding import Binding, BindingsMap
from textual.widgets import Footer, DataTable, Static
from textual.notifications import Notification
from datetime import datetime

from schedule.config import load_config, DateFieldManager
from schedule.taskwarrior import TaskWarriorClient
from schedule.widgets.report_modal import ReportModal
from schedule.widgets.custom_header import CustomHeader


def format_date(date_str: str) -> str:
    if not date_str or date_str == "-":
        return "-"
    try:
        dt = datetime.strptime(date_str[:8], "%Y%m%d")
        return dt.strftime("%a %d-%m-%Y")
    except (ValueError, IndexError):
        return date_str


class ScheduleApp(App):
    """Main application class for schedule TUI."""

    TITLE = "Schedule"
    SUBTITLE = "TaskWarrior Task Rescheduler"

    CSS_PATH = "app.tcss"

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("tab", "toggle_selection", "Select", show=True),
        Binding("shift+a", "select_all", "All", show=True),
        Binding("s", "toggle_scheduled", "scheduled", show=True),
        Binding("d", "toggle_due", "due", show=True),
        Binding("w", "toggle_wait", "wait", show=True),
        Binding("0", "clear_date", "clear", show=True),
        Binding("1", "schedule_1", "1", show=True),
        Binding("2", "schedule_2", "2", show=True),
        Binding("3", "schedule_3", "3", show=True),
        Binding("4", "schedule_4", "4", show=True),
        Binding("5", "schedule_5", "5", show=True),
        Binding("6", "schedule_6", "6", show=False),
        Binding("7", "schedule_7", "7", show=False),
        Binding("8", "schedule_8", "8", show=False),
        Binding("9", "schedule_9", "9", show=False),
        Binding("r", "change_filter", "filter", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self):
        self.config = load_config()
        self.date_field_mgr = DateFieldManager(
            self.config.get("default_date_fields", ["scheduled"])
        )
        self.current_filter = self.config.get("default_report", "next")

        super().__init__()

        self._update_binding_descriptions()

        self.tw_client = TaskWarriorClient()
        self.tasks = []
        self.selected_tasks: set[str] = set()
        self.columns_added = False

    def _update_binding_descriptions(self) -> None:
        hotkeys = self.config.get("hotkeys", {})
        updated_bindings = []

        for _, binding in self._bindings:
            if binding.action.startswith("schedule_") and len(binding.action) == 10:
                key = binding.action[-1]
                if key in hotkeys:
                    updated_bindings.append(
                        Binding(
                            binding.key,
                            binding.action,
                            hotkeys[key],
                            show=True,
                            key_display=binding.key_display,
                            priority=binding.priority,
                            tooltip=binding.tooltip,
                        )
                    )
                else:
                    updated_bindings.append(
                        Binding(
                            binding.key,
                            binding.action,
                            binding.description,
                            show=False,
                            key_display=binding.key_display,
                            priority=binding.priority,
                            tooltip=binding.tooltip,
                        )
                    )
            else:
                updated_bindings.append(binding)

        self._bindings = BindingsMap(updated_bindings)
        self.refresh_bindings()

    def compose(self) -> ComposeResult:
        active_fields = (
            ", ".join(self.date_field_mgr.get_active())
            if self.date_field_mgr.get_active()
            else "None"
        )
        yield CustomHeader(filter_text=self.current_filter, active_fields=active_fields)
        yield DataTable(id="task-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#task-table", DataTable)

        if not self.columns_added:
            table.add_columns(
                "ID", "Description", "Project", "Scheduled", "Due", "Wait"
            )
            self.columns_added = True

        try:
            self.tasks = self.tw_client.get_tasks(self.current_filter)

            if self.tasks:
                for task in self.tasks:
                    task_uuid = task.get("uuid", "")
                    if not task_uuid:
                        continue

                    row_data = [
                        str(task.get("id", "")),
                        task.get("description", "")[:50],
                        task.get("project", ""),
                        format_date(task.get("scheduled", "-")),
                        format_date(task.get("due", "-")),
                        format_date(task.get("wait", "-")),
                    ]
                    table.add_row(*row_data, key=task_uuid)
            else:
                table.add_row("", "No tasks", "", "", "", "", key="empty")
        except Exception as e:
            self.log(f"Error loading tasks: {e}", exc_info=True)
            table.add_row("", f"Error: {str(e)}", "", "", "", "", key="error")

    def action_toggle_selection(self) -> None:
        """Toggle selection of current cursor row."""
        table = self.query_one("#task-table", DataTable)

        if table.row_count == 0:
            return

        if not table.is_valid_coordinate(table.cursor_coordinate):
            return

        row_index = table.cursor_row
        if row_index < 0 or row_index >= len(self.tasks):
            return

        task = self.tasks[row_index]
        task_uuid = task.get("uuid", "")

        if not task_uuid:
            return

        if task_uuid in self.selected_tasks:
            self.selected_tasks.remove(task_uuid)
        else:
            self.selected_tasks.add(task_uuid)

        self._update_row_styling(task_uuid, task.get("id", ""))

    def action_select_all(self) -> None:
        """Select all visible tasks."""
        for task in self.tasks:
            task_uuid = task.get("uuid", "")
            if task_uuid:
                self.selected_tasks.add(task_uuid)

        for task in self.tasks:
            task_uuid = task.get("uuid", "")
            if task_uuid:
                self._update_row_styling(task_uuid, task.get("id", ""))

    def _update_row_styling(self, task_uuid: str, task_id: str) -> None:
        table = self.query_one("#task-table", DataTable)

        try:
            if task_uuid in self.selected_tasks:
                table.update_cell(task_uuid, "ID", f"● {task_id}")
            else:
                table.update_cell(task_uuid, "ID", task_id)
        except Exception as e:
            self.log(f"Error updating row styling for {task_uuid}: {e}", exc_info=True)

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

        table = self.query_one("#task-table", DataTable)

        if table.row_count == 0:
            return []

        if not table.is_valid_coordinate(table.cursor_coordinate):
            return []

        row_index = table.cursor_row
        if 0 <= row_index < len(self.tasks):
            task_uuid = self.tasks[row_index].get("uuid", "")
            if task_uuid:
                return [task_uuid]

        return []

    def clear_selection(self) -> None:
        """Clear all selection and remove visual indicators."""
        self.selected_tasks.clear()

        for task in self.tasks:
            task_uuid = task.get("uuid", "")
            if task_uuid:
                self._update_row_styling(task_uuid, str(task.get("id", "")))

    def _update_info_bar(self) -> None:
        header = self.query_one(CustomHeader)
        active_fields = (
            ", ".join(self.date_field_mgr.get_active())
            if self.date_field_mgr.get_active()
            else "None"
        )
        header.update_status(self.current_filter, active_fields)

    def refresh_tasks(self) -> None:
        try:
            table = self.query_one("#task-table", DataTable)

            old_cursor_row = table.cursor_row if table.row_count > 0 else 0

            self.tasks = self.tw_client.get_tasks(self.current_filter)

            table.clear()

            if self.tasks:
                for task in self.tasks:
                    task_uuid = task.get("uuid", "")
                    if not task_uuid:
                        continue

                    row_data = [
                        str(task.get("id", "")),
                        task.get("description", "")[:50],
                        task.get("project", ""),
                        format_date(task.get("scheduled", "-")),
                        format_date(task.get("due", "-")),
                        format_date(task.get("wait", "-")),
                    ]
                    table.add_row(*row_data, key=task_uuid)

                if table.row_count > 0:
                    safe_row = min(old_cursor_row, table.row_count - 1)
                    table.move_cursor(row=safe_row, scroll=True, animate=False)
            else:
                table.add_row("", "No tasks", "", "", "", "", key="empty")
        except Exception as e:
            self.log(f"Error refreshing tasks: {e}", exc_info=True)
            self.notify(f"Error refreshing tasks: {str(e)}", severity="error")

    def _show_error(self, message: str) -> None:
        """Show error notification to user."""
        self.notify(message, severity="error")

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
        if not self.date_field_mgr.get_active():
            self._show_error("No active date fields to clear")
            return

        selected_uuids = self.get_selected_tasks()
        if not selected_uuids:
            self._show_error("No tasks selected")
            return

        for uuid in selected_uuids:
            modifications = {field: "" for field in self.date_field_mgr.get_active()}
            success, stderr = self.tw_client.modify_task(uuid, **modifications)
            if not success:
                self.log(
                    f"Failed to clear dates for task {uuid}: {stderr}", exc_info=True
                )
                error_msg = (
                    f"Failed to clear dates: {stderr}"
                    if stderr
                    else f"Failed to clear dates for task {uuid[:8]}"
                )
                self._show_error(error_msg)

        self.clear_selection()
        self.refresh_tasks()

    def action_schedule_1(self) -> None:
        self._schedule_with_hotkey("1")

    def action_schedule_2(self) -> None:
        self._schedule_with_hotkey("2")

    def action_schedule_3(self) -> None:
        self._schedule_with_hotkey("3")

    def action_schedule_4(self) -> None:
        self._schedule_with_hotkey("4")

    def action_schedule_5(self) -> None:
        self._schedule_with_hotkey("5")

    def action_schedule_6(self) -> None:
        self._schedule_with_hotkey("6")

    def action_schedule_7(self) -> None:
        self._schedule_with_hotkey("7")

    def action_schedule_8(self) -> None:
        self._schedule_with_hotkey("8")

    def action_schedule_9(self) -> None:
        self._schedule_with_hotkey("9")

    def _schedule_with_hotkey(self, hotkey: str) -> None:
        if hotkey not in self.config.get("hotkeys", {}):
            self._show_error(f"Hotkey {hotkey} not configured")
            return

        hotkey_value = self.config["hotkeys"][hotkey]

        active_fields = self.date_field_mgr.get_active()
        if not active_fields:
            self._show_error("No active date fields. Use W/S/D to toggle.")
            return

        selected_uuids = self.get_selected_tasks()
        if not selected_uuids:
            self._show_error("No tasks selected")
            return

        for uuid in selected_uuids:
            modifications = {field: hotkey_value for field in active_fields}
            success, stderr = self.tw_client.modify_task(uuid, **modifications)
            if not success:
                self.log(f"Failed to schedule task {uuid}: {stderr}", exc_info=True)
                error_msg = (
                    f"Failed to schedule: {stderr}"
                    if stderr
                    else f"Failed to schedule task {uuid[:8]}"
                )
                self._show_error(error_msg)

        self.clear_selection()
        self.refresh_tasks()

    def action_change_filter(self) -> None:
        def on_report_result(result: str | None) -> None:
            if result is not None:
                self.current_filter = result
                self._update_info_bar()
                self.refresh_tasks()

        self.push_screen(ReportModal(), callback=on_report_result)
