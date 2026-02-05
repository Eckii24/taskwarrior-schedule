"""TaskWarrior integration module."""

import json
import subprocess
from typing import Any, Dict, List


class TaskWarrior:
    """Interface to TaskWarrior CLI."""

    def __init__(self) -> None:
        """Initialize TaskWarrior interface."""
        self.command = "task"

    def export(self, report: str = "next") -> List[Dict[str, Any]]:
        """Export tasks from TaskWarrior in JSON format.

        Args:
            report: TaskWarrior report name (default: "next")

        Returns:
            List of task dictionaries
        """
        try:
            result = subprocess.run(
                [self.command, report, "export"],
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return []

    def modify(self, task_id: int, changes: Dict[str, Any]) -> bool:
        """Modify a task in TaskWarrior.

        Args:
            task_id: Task ID to modify
            changes: Dictionary of field changes

        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [self.command, str(task_id), "modify"]
            for key, value in changes.items():
                cmd.append(f"{key}={value}")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
