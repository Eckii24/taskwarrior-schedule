"""TaskWarrior integration module."""

import json
import subprocess
from typing import Any, Dict, List


class TaskWarriorClient:
    """Interface to TaskWarrior CLI via subprocess."""

    def __init__(self) -> None:
        """Initialize TaskWarrior client."""
        self.command = "task"

    def get_tasks(self, report: str) -> List[Dict[str, Any]]:
        """Get tasks from a TaskWarrior report via JSON export.

        Runs `task export <report>` and parses JSON output.
        Dates are returned as ISO-8601 strings (no conversion).

        Args:
            report: TaskWarrior report name (e.g., "next", "all")

        Returns:
            List of task dictionaries with string values (including dates)

        Raises:
            FileNotFoundError: If TaskWarrior is not installed
            subprocess.CalledProcessError: If report is invalid or export fails
        """
        result = subprocess.run(
            [self.command, "export", report],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, [self.command, "export", report], result.stderr
            )

        return json.loads(result.stdout)

    def modify_task(self, uuid: str, **modifications: Any) -> bool:
        """Modify a task in TaskWarrior.

        Runs `task uuid:<uuid> modify key:value ...` with confirmation disabled.

        Args:
            uuid: Task UUID to modify
            **modifications: Key-value pairs for task fields (e.g., scheduled='tomorrow')

        Returns:
            True if successful, False if modification fails
        """
        try:
            cmd = [self.command, f"uuid:{uuid}", "modify"]
            for key, value in modifications.items():
                cmd.append(f"{key}:{value}")
            cmd.extend(["rc.confirmation:off"])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )

            return result.returncode == 0
        except Exception:
            return False
