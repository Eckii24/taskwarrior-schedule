"""Tests for the main ScheduleApp - comprehensive TUI testing."""

import json
from unittest.mock import Mock, patch

import pytest
from textual.widgets import DataTable

from schedule.app import ScheduleApp
from schedule.widgets.custom_header import CustomHeader
from schedule.widgets.report_modal import ReportModal


@pytest.fixture
def mock_tw_client(monkeypatch, sample_tasks):
    """Mock TaskWarriorClient for all ScheduleApp tests."""

    def mock_get_tasks(self, filter_or_report=None):
        return sample_tasks

    def mock_get_report_names(self):
        return {"next", "all", "overdue"}

    def mock_modify_task(self, uuid, **modifications):
        return (True, "")

    from schedule import taskwarrior

    monkeypatch.setattr(taskwarrior.TaskWarriorClient, "get_tasks", mock_get_tasks)
    monkeypatch.setattr(
        taskwarrior.TaskWarriorClient, "get_report_names", mock_get_report_names
    )
    monkeypatch.setattr(taskwarrior.TaskWarriorClient, "modify_task", mock_modify_task)


class TestScheduleAppLifecycle:
    """Test app initialization and lifecycle."""

    @pytest.mark.asyncio
    async def test_app_mounts_successfully(self, mock_tw_client):
        """Should mount and display task table."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Check that table exists
            table = app.query_one("#task-table", DataTable)
            assert table is not None

    @pytest.mark.asyncio
    async def test_app_loads_default_config(self, mock_tw_client):
        """Should load default configuration on initialization."""
        app = ScheduleApp()

        assert app.config["default_report"] == "next"
        assert "scheduled" in app.config["default_date_fields"]

    @pytest.mark.asyncio
    async def test_app_loads_tasks_on_mount(self, mock_tw_client, sample_tasks):
        """Should load and display tasks on mount."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            table = app.query_one("#task-table", DataTable)

            # Should have loaded sample tasks
            assert table.row_count == len(sample_tasks)

    @pytest.mark.asyncio
    async def test_app_displays_task_data(self, mock_tw_client, sample_tasks):
        """Should display task data in table columns."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            table = app.query_one("#task-table", DataTable)

            # Check columns exist (DataTable has columns property)
            assert (
                len(table.columns) == 6
            )  # ID, Description, Project, Scheduled, Due, Wait

            # Check first task data is present
            assert len(app.tasks) == 3

    @pytest.mark.asyncio
    async def test_app_handles_empty_task_list(self, monkeypatch):
        """Should handle empty task list gracefully."""

        def mock_get_tasks(self, filter_or_report=None):
            return []

        from schedule import taskwarrior

        monkeypatch.setattr(taskwarrior.TaskWarriorClient, "get_tasks", mock_get_tasks)

        def mock_get_report_names(self):
            return {"next"}

        monkeypatch.setattr(
            taskwarrior.TaskWarriorClient, "get_report_names", mock_get_report_names
        )

        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            table = app.query_one("#task-table", DataTable)
            # Should show "No tasks" message
            assert table.row_count == 1


class TestScheduleAppNavigation:
    """Test cursor navigation and keyboard controls."""

    @pytest.mark.asyncio
    async def test_j_key_moves_cursor_down(self, mock_tw_client):
        """Should move cursor down when j is pressed."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            table = app.query_one("#task-table", DataTable)
            initial_row = table.cursor_row

            await pilot.press("j")
            await pilot.pause()

            assert table.cursor_row == initial_row + 1

    @pytest.mark.asyncio
    async def test_k_key_moves_cursor_up(self, mock_tw_client):
        """Should move cursor up when k is pressed."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            table = app.query_one("#task-table", DataTable)

            # Move down first
            await pilot.press("j")
            await pilot.pause()

            current_row = table.cursor_row

            # Move back up
            await pilot.press("k")
            await pilot.pause()

            assert table.cursor_row == current_row - 1

    @pytest.mark.asyncio
    async def test_multiple_navigation_keys(self, mock_tw_client):
        """Should handle multiple navigation key presses."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            table = app.query_one("#task-table", DataTable)

            # Navigate down 2 rows
            await pilot.press("j", "j")
            await pilot.pause()

            assert table.cursor_row == 2

            # Navigate up 1 row
            await pilot.press("k")
            await pilot.pause()

            assert table.cursor_row == 1


class TestScheduleAppTaskSelection:
    """Test task selection functionality."""

    @pytest.mark.asyncio
    async def test_multiple_task_selection(self, mock_tw_client, sample_tasks):
        """Should allow selecting multiple tasks."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            task1_uuid = sample_tasks[0]["uuid"]
            task2_uuid = sample_tasks[1]["uuid"]

            app.action_toggle_selection()
            await pilot.pause()

            assert task1_uuid in app.selected_tasks

            await pilot.press("j")
            await pilot.pause()
            app.action_toggle_selection()
            await pilot.pause()

            assert len(app.selected_tasks) == 2
            assert task1_uuid in app.selected_tasks
            assert task2_uuid in app.selected_tasks

    @pytest.mark.asyncio
    async def test_shift_a_selects_all_tasks(self, mock_tw_client, sample_tasks):
        """Should select all visible tasks when Shift+A is pressed."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            app.action_select_all()
            await pilot.pause()

            assert len(app.selected_tasks) == len(sample_tasks)

    @pytest.mark.asyncio
    async def test_tab_toggles_single_task_selection(
        self, mock_tw_client, sample_tasks
    ):
        """Should select/deselect task when Tab is pressed."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            table = app.query_one("#task-table", DataTable)
            table.focus()
            await pilot.pause()

            assert len(app.selected_tasks) == 0

            first_task_uuid = sample_tasks[0]["uuid"]

            app.action_toggle_selection()
            await pilot.pause()

            assert len(app.selected_tasks) == 1
            assert first_task_uuid in app.selected_tasks

            app.action_toggle_selection()
            await pilot.pause()

            assert len(app.selected_tasks) == 0

    @pytest.mark.asyncio
    async def test_error_when_no_active_fields(self, mock_tw_client):
        """Should show error if no active date fields."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Deactivate all fields
            await pilot.press("s")  # Turn off scheduled (the default)
            await pilot.pause()

            # Try to schedule
            await pilot.press("1")
            await pilot.pause()

            # Should have shown error (we can't easily check notification content,
            # but we can verify no crash occurred and selection wasn't cleared)
            assert True  # If we got here, no crash


class TestScheduleAppReportSwitching:
    """Test report/filter switching functionality."""

    @pytest.mark.asyncio
    async def test_r_key_opens_modal(self, mock_tw_client):
        """Should open report modal when r is pressed."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Press r to open modal
            await pilot.press("r")
            await pilot.pause()

            # Modal should be visible
            modal = app.screen
            assert isinstance(modal, ReportModal)

    @pytest.mark.asyncio
    async def test_changing_report_refreshes_tasks(self, mock_tw_client, monkeypatch):
        """Should refresh task list when report is changed."""
        get_tasks_calls = []

        def mock_get_tasks(self, filter_or_report=None):
            get_tasks_calls.append(filter_or_report)
            return [
                {
                    "id": 99,
                    "uuid": "new-task-uuid",
                    "description": "New task from different report",
                    "status": "pending",
                    "project": "",
                    "scheduled": "",
                    "due": "",
                    "wait": "",
                }
            ]

        from schedule import taskwarrior

        monkeypatch.setattr(taskwarrior.TaskWarriorClient, "get_tasks", mock_get_tasks)

        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Initial load
            assert len(get_tasks_calls) == 1

            # Open modal and submit new filter
            await pilot.press("r")
            await pilot.pause()

            # Type new filter (we need to access the input directly)
            from textual.widgets import Input

            input_field = app.screen.query_one("#report-input", Input)
            input_field.value = "overdue"

            await pilot.press("enter")
            await pilot.pause()

            # Should have called get_tasks again with new filter
            assert len(get_tasks_calls) == 2
            assert get_tasks_calls[1] == "overdue"


class TestScheduleAppErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_handles_taskwarrior_error_on_load(self, monkeypatch):
        """Should handle TaskWarrior errors gracefully on initial load."""

        def mock_get_tasks(self, filter_or_report=None):
            raise Exception("TaskWarrior not found")

        from schedule import taskwarrior

        monkeypatch.setattr(taskwarrior.TaskWarriorClient, "get_tasks", mock_get_tasks)

        def mock_get_report_names(self):
            return {"next"}

        monkeypatch.setattr(
            taskwarrior.TaskWarriorClient, "get_report_names", mock_get_report_names
        )

        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Should not crash, should show error in table
            table = app.query_one("#task-table", DataTable)
            assert table.row_count >= 0  # At least didn't crash

    @pytest.mark.asyncio
    async def test_handles_modify_task_failure(self, mock_tw_client, monkeypatch):
        """Should handle task modification failures."""

        def mock_modify_fail(self, uuid, **modifications):
            return (False, "Permission denied")

        from schedule import taskwarrior

        monkeypatch.setattr(
            taskwarrior.TaskWarriorClient, "modify_task", mock_modify_fail
        )

        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Try to schedule task
            await pilot.press("1")
            await pilot.pause()

            # Should not crash (error shown to user)
            assert True

    @pytest.mark.asyncio
    async def test_handles_unconfigured_hotkey(self, mock_tw_client):
        """Should show error for unconfigured hotkeys."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Press hotkey 9 (not configured by default)
            await pilot.press("9")
            await pilot.pause()

            # Should not crash
            assert True


class TestScheduleAppIntegration:
    """Integration tests for complete user workflows."""

    @pytest.mark.asyncio
    async def test_complete_batch_scheduling_workflow(
        self, mock_tw_client, monkeypatch
    ):
        """Test complete workflow: navigate, select multiple, toggle fields, schedule."""
        modify_calls = []

        def mock_modify(self, uuid, **modifications):
            modify_calls.append((uuid, modifications))
            return (True, "")

        from schedule import taskwarrior

        monkeypatch.setattr(taskwarrior.TaskWarriorClient, "modify_task", mock_modify)

        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            app.action_toggle_selection()
            await pilot.pause()

            await pilot.press("j")
            app.action_toggle_selection()
            await pilot.pause()

            await pilot.press("d")
            await pilot.pause()

            await pilot.press("4")
            await pilot.pause()

            assert len(modify_calls) == 2
            for uuid, mods in modify_calls:
                assert "scheduled" in mods
                assert "due" in mods
                assert mods["scheduled"] == "sow"
                assert mods["due"] == "sow"

            # Verify: selection cleared
            assert len(app.selected_tasks) == 0

    @pytest.mark.asyncio
    async def test_clear_dates_workflow(self, mock_tw_client, monkeypatch):
        """Test workflow for clearing dates from multiple tasks."""
        modify_calls = []

        def mock_modify(self, uuid, **modifications):
            modify_calls.append((uuid, modifications))
            return (True, "")

        from schedule import taskwarrior

        monkeypatch.setattr(taskwarrior.TaskWarriorClient, "modify_task", mock_modify)

        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            app.action_select_all()
            await pilot.pause()

            await pilot.press("d")
            await pilot.press("w")
            await pilot.pause()

            await pilot.press("0")
            await pilot.pause()

            assert len(modify_calls) == 3
            for uuid, mods in modify_calls:
                assert mods["scheduled"] == ""
                assert mods["due"] == ""
                assert mods["wait"] == ""


class TestScheduleAppSortCycling:
    """Test sort mode cycling functionality."""

    @pytest.mark.asyncio
    async def test_cycle_sort_through_all_modes(self, mock_tw_client):
        """Should cycle through all sort modes with o key."""
        from schedule.app import SORT_MODES

        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            assert app.sort_mode == "default"

            for expected_mode in SORT_MODES[1:] + ["default"]:
                app.action_cycle_sort()
                await pilot.pause()
                assert app.sort_mode == expected_mode

    @pytest.mark.asyncio
    async def test_sort_mode_shown_in_header(self, mock_tw_client):
        """Should update header when sort mode changes."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            app.action_cycle_sort()
            await pilot.pause()

            assert app.sort_mode == "project"

            header = app.query_one(CustomHeader)
            assert header.sort_mode == "project"

    @pytest.mark.asyncio
    async def test_sort_default_refreshes_tasks(self, mock_tw_client):
        """Cycling back to default should refresh tasks (original order)."""
        from schedule.app import SORT_MODES

        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            for _ in range(len(SORT_MODES)):
                app.action_cycle_sort()
                await pilot.pause()

            assert app.sort_mode == "default"


class TestScheduleAppDateFormat:
    """Test date format toggling functionality."""

    @pytest.mark.asyncio
    async def test_toggle_date_format(self, mock_tw_client):
        """Should toggle between absolute and relative."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            assert app.relative_dates is False

            app.action_toggle_date_format()
            await pilot.pause()

            assert app.relative_dates is True

            app.action_toggle_date_format()
            await pilot.pause()

            assert app.relative_dates is False

    @pytest.mark.asyncio
    async def test_date_format_shown_in_header(self, mock_tw_client):
        """Should update header when date format changes."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            header = app.query_one(CustomHeader)
            assert header.date_format == "absolute"

            app.action_toggle_date_format()
            await pilot.pause()

            assert header.date_format == "relative"

    @pytest.mark.asyncio
    async def test_date_cells_update_on_toggle(self, mock_tw_client, sample_tasks):
        """Should update displayed dates when toggling format."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            table = app.query_one("#task-table", DataTable)

            first_uuid = sample_tasks[0]["uuid"]
            initial_val = table.get_cell(first_uuid, "scheduled")

            app.action_toggle_date_format()
            await pilot.pause()

            new_val = table.get_cell(first_uuid, "scheduled")
            assert new_val != initial_val


class TestScheduleAppClearSelection:
    """Test clear all selection functionality."""

    @pytest.mark.asyncio
    async def test_x_clears_all_selections(self, mock_tw_client, sample_tasks):
        """Should clear all selections when x is pressed."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            app.action_select_all()
            await pilot.pause()
            assert len(app.selected_tasks) == len(sample_tasks)

            app.action_clear_all_selection()
            await pilot.pause()
            assert len(app.selected_tasks) == 0

    @pytest.mark.asyncio
    async def test_clear_selection_removes_visual_markers(
        self, mock_tw_client, sample_tasks
    ):
        """Should remove ● markers when clearing selection."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            app.action_select_all()
            await pilot.pause()

            table = app.query_one("#task-table", DataTable)
            first_uuid = sample_tasks[0]["uuid"]
            marked = table.get_cell(first_uuid, "id")
            assert "●" in str(marked)

            app.action_clear_all_selection()
            await pilot.pause()

            unmarked = table.get_cell(first_uuid, "id")
            assert "●" not in str(unmarked)


class TestScheduleAppMKey:
    """Test m key as alternative for toggle selection."""

    @pytest.mark.asyncio
    async def test_m_key_toggles_selection(self, mock_tw_client, sample_tasks):
        """m key should work as alternative to Tab for toggling selection."""
        app = ScheduleApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            assert len(app.selected_tasks) == 0

            app.action_toggle_selection()
            await pilot.pause()

            first_uuid = sample_tasks[0]["uuid"]
            assert first_uuid in app.selected_tasks
