"""Tests for taskwarrior.py - TaskWarrior CLI integration."""

import json
import subprocess
from unittest.mock import Mock, patch

import pytest

from schedule.taskwarrior import TaskWarriorClient


class TestTaskWarriorClient:
    """Test TaskWarrior CLI client."""

    def test_initialization(self):
        """Should initialize with default command."""
        client = TaskWarriorClient()

        assert client.command == "task"
        assert client._report_cache is None

    def test_get_report_names_success(self, monkeypatch):
        """Should parse report names from _config output."""
        mock_output = """
report.next.columns=id,description
report.all.filter=status:pending
report.overdue.labels=ID,Description
report.custom.description=Custom report
color.active=bold
"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = mock_output
        mock_result.stderr = ""

        monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

        client = TaskWarriorClient()
        reports = client.get_report_names()

        assert "next" in reports
        assert "all" in reports
        assert "overdue" in reports
        assert "custom" in reports
        assert "color" not in reports  # Not a report

    def test_get_report_names_caching(self, monkeypatch):
        """Should cache report names for performance."""
        call_count = 0

        def mock_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            result = Mock()
            result.returncode = 0
            result.stdout = "report.next.columns=id\n"
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()

        # First call - should execute
        reports1 = client.get_report_names()
        assert call_count == 1

        # Second call - should use cache
        reports2 = client.get_report_names()
        assert call_count == 1  # No additional call
        assert reports1 == reports2

    def test_get_report_names_cache_expiry(self, monkeypatch):
        """Should refresh cache after TTL expires."""
        import time

        call_count = 0

        def mock_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            result = Mock()
            result.returncode = 0
            result.stdout = "report.next.columns=id\n"
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()
        client._report_cache_ttl = 0.1  # 100ms TTL

        # First call
        client.get_report_names()
        assert call_count == 1

        # Wait for cache to expire
        time.sleep(0.2)

        # Second call - cache expired
        client.get_report_names()
        assert call_count == 2

    def test_get_report_names_command_failure(self, monkeypatch):
        """Should raise exception on command failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Error message"

        monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

        client = TaskWarriorClient()

        with pytest.raises(subprocess.CalledProcessError):
            client.get_report_names()

    def test_get_tasks_with_none_defaults_to_next(self, monkeypatch):
        """Should default to 'next' report when filter_or_report is None."""
        captured_cmd = []
        call_count = [0]

        def mock_run(cmd, *args, **kwargs):
            captured_cmd.append(cmd)
            result = Mock()
            result.returncode = 0

            # First call is for _config (getting report names)
            if call_count[0] == 0:
                result.stdout = "report.next.columns=id\n"
                call_count[0] += 1
            else:
                # Second call is the actual export
                result.stdout = "[]"

            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()

        client.get_tasks(None)

        # Should use "next" report (second command)
        assert len(captured_cmd) == 2  # _config + export
        assert "export" in captured_cmd[1]
        assert "next" in captured_cmd[1]

    def test_get_tasks_with_empty_string_exports_all(self, monkeypatch):
        """Should export all tasks when filter_or_report is empty string."""
        captured_cmd = []

        def mock_run(cmd, *args, **kwargs):
            captured_cmd.append(cmd)
            result = Mock()
            result.returncode = 0
            result.stdout = "[]"
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()

        client.get_tasks("")

        # Should just call export without filter
        assert captured_cmd[0][-1] == "export"

    def test_get_tasks_with_known_report(self, monkeypatch):
        """Should use report name if last token is a known report."""
        captured_cmd = []
        call_count = [0]

        def mock_run(cmd, *args, **kwargs):
            captured_cmd.append(cmd)
            result = Mock()
            result.returncode = 0

            if call_count[0] == 0:
                result.stdout = "report.next.columns=id\nreport.overdue.columns=id\n"
                call_count[0] += 1
            else:
                result.stdout = "[]"

            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()

        client.get_tasks("overdue")

        assert len(captured_cmd) == 2
        assert "export" in captured_cmd[1]
        assert "overdue" in captured_cmd[1]

    def test_get_tasks_with_filter_and_report(self, monkeypatch):
        """Should handle filter tokens before report name."""
        captured_cmd = []
        call_count = [0]

        def mock_run(cmd, *args, **kwargs):
            captured_cmd.append(cmd)
            result = Mock()
            result.returncode = 0

            if call_count[0] == 0:
                result.stdout = "report.next.columns=id\n"
                call_count[0] += 1
            else:
                result.stdout = "[]"

            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()

        client.get_tasks("project:work status:pending next")

        cmd = captured_cmd[1]  # Second command is the export
        assert "project:work" in cmd
        assert "status:pending" in cmd
        assert "export" in cmd
        assert "next" in cmd

    def test_get_tasks_with_unknown_filter(self, monkeypatch):
        """Should treat entire string as filter if no known report."""
        captured_cmd = []
        call_count = [0]

        def mock_run(cmd, *args, **kwargs):
            captured_cmd.append(cmd)
            result = Mock()
            result.returncode = 0

            if call_count[0] == 0:
                result.stdout = "report.next.columns=id\n"
                call_count[0] += 1
            else:
                result.stdout = "[]"

            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()

        client.get_tasks("status:pending")

        cmd = captured_cmd[1]  # Second command
        assert "status:pending" in cmd
        assert "export" in cmd

    def test_get_tasks_returns_parsed_json(self, monkeypatch):
        """Should parse and return JSON task data."""
        sample_tasks = [
            {"id": 1, "description": "Task 1", "status": "pending"},
            {"id": 2, "description": "Task 2", "status": "pending"},
        ]

        def mock_run(cmd, *args, **kwargs):
            result = Mock()
            result.returncode = 0
            result.stdout = json.dumps(sample_tasks)
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()
        client._report_cache = {"next"}

        tasks = client.get_tasks("next")

        assert len(tasks) == 2
        assert tasks[0]["description"] == "Task 1"
        assert tasks[1]["id"] == 2

    def test_get_tasks_command_failure(self, monkeypatch):
        """Should raise exception on command failure."""

        def mock_run(cmd, *args, **kwargs):
            result = Mock()
            result.returncode = 1
            result.stderr = "TaskWarrior error"
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()
        client._report_cache = {"next"}

        with pytest.raises(subprocess.CalledProcessError):
            client.get_tasks("next")

    def test_modify_task_success(self, monkeypatch):
        """Should successfully modify task and return success."""
        captured_cmd = []

        def mock_run(cmd, *args, **kwargs):
            captured_cmd.append(cmd)
            result = Mock()
            result.returncode = 0
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()
        uuid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

        success, stderr = client.modify_task(uuid, scheduled="tomorrow", due="+1w")

        assert success is True
        assert stderr == ""

        cmd = captured_cmd[0]
        assert f"uuid:{uuid}" in cmd
        assert "modify" in cmd
        assert "scheduled:tomorrow" in cmd
        assert "due:+1w" in cmd

    def test_modify_task_failure(self, monkeypatch):
        """Should return failure status and stderr on error."""

        def mock_run(cmd, *args, **kwargs):
            result = Mock()
            result.returncode = 1
            result.stderr = "Cannot modify task"
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()
        uuid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

        success, stderr = client.modify_task(uuid, scheduled="invalid")

        assert success is False
        assert stderr == "Cannot modify task"

    def test_modify_task_with_empty_value(self, monkeypatch):
        """Should handle empty values for clearing fields."""
        captured_cmd = []

        def mock_run(cmd, *args, **kwargs):
            captured_cmd.append(cmd)
            result = Mock()
            result.returncode = 0
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()
        uuid = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"

        client.modify_task(uuid, scheduled="", due="")

        cmd = captured_cmd[0]
        assert "scheduled:" in cmd
        assert "due:" in cmd

    def test_modify_task_uses_correct_rc_options(self, monkeypatch):
        """Should use proper TaskWarrior rc options."""
        captured_cmd = []

        def mock_run(cmd, *args, **kwargs):
            captured_cmd.append(cmd)
            result = Mock()
            result.returncode = 0
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()
        uuid = "test-uuid"

        client.modify_task(uuid, test="value")

        cmd = captured_cmd[0]
        assert "rc.confirmation=off" in cmd
        assert "rc.bulk=0" in cmd
        assert "rc.recurrence.confirmation=no" in cmd
        assert "rc.hooks=0" in cmd

    def test_modify_task_multiple_fields(self, monkeypatch):
        """Should handle modifying multiple fields at once."""
        captured_cmd = []

        def mock_run(cmd, *args, **kwargs):
            captured_cmd.append(cmd)
            result = Mock()
            result.returncode = 0
            result.stderr = ""
            return result

        monkeypatch.setattr(subprocess, "run", mock_run)

        client = TaskWarriorClient()
        uuid = "test-uuid"

        client.modify_task(
            uuid, scheduled="tomorrow", due="+2d", wait="sow", priority="H"
        )

        cmd = captured_cmd[0]
        assert "scheduled:tomorrow" in cmd
        assert "due:+2d" in cmd
        assert "wait:sow" in cmd
        assert "priority:H" in cmd
