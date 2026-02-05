"""TaskWarrior integration module."""

import json
import re
import shlex
import subprocess
import time
from typing import Any, Dict, List, Optional, Set


class TaskWarriorClient:
    """Interface to TaskWarrior CLI via subprocess."""

    def __init__(self) -> None:
        """Initialize TaskWarrior client."""
        self.command = "task"
        self._report_cache: Optional[Set[str]] = None
        self._report_cache_time: float = 0.0
        self._report_cache_ttl: float = 15.0  # 15 seconds cache TTL

    def get_report_names(self) -> Set[str]:
        """Get available TaskWarrior report names.

        Runs `task rc.hooks=0 _config` and parses report names from output.
        Results are cached for performance (15 second TTL).

        Returns:
            Set of report names available in TaskWarrior

        Raises:
            subprocess.CalledProcessError: If command fails
        """
        now = time.time()
        if (
            self._report_cache is not None
            and (now - self._report_cache_time) < self._report_cache_ttl
        ):
            return self._report_cache

        result = subprocess.run(
            [self.command, "rc.confirmation=off", "rc.hooks=0", "_config"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                [self.command, "rc.confirmation=off", "rc.hooks=0", "_config"],
                result.stderr,
            )

        # Parse report names using regex: report.<name>.<field>=value or report.<name>.<field>
        report_names = set()
        for line in result.stdout.splitlines():
            match = re.match(r"^report\.([^.]+)\.[^=]+(?:=|$)", line)
            if match:
                report_names.add(match.group(1))

        self._report_cache = report_names
        self._report_cache_time = now

        return report_names

    def get_tasks(self, filter_or_report: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tasks from TaskWarrior using filter or report.

        Implements filter/report determination logic from taskwarrior-web:
        - If filter_or_report is None/undefined, defaults to "next"
        - If filter_or_report is empty string "", exports all tasks
        - If last token matches a known report name, treats it as report
        - Otherwise treats entire string as filter expression

        Args:
            filter_or_report: Filter expression or report name
                            (e.g., "next", "status:pending", "project:foo next")

        Returns:
            List of task dictionaries with string values (including dates)

        Raises:
            subprocess.CalledProcessError: If TaskWarrior command fails
        """
        # Default to "next" if not provided (preserve "" as valid filter for "export all")
        normalized = "next" if filter_or_report is None else filter_or_report.strip()

        # Tokenize input
        tokens = normalized.split() if normalized else []

        # Determine if last token is a report name
        report = None
        filter_tokens = []

        if tokens:
            # Fetch known report names (cached)
            report_names = self.get_report_names()
            maybe_report = tokens[-1]

            if maybe_report in report_names:
                # Last token is a report
                report = maybe_report
                filter_tokens = tokens[:-1]
            else:
                # Not a report, treat entire string as filter
                filter_tokens = tokens

        # Build command arguments
        cmd = [self.command, "rc.confirmation=off", "rc.hooks=0"]

        if report:
            # Format: task <filters...> export <report>
            if filter_tokens:
                cmd.extend(filter_tokens)
            cmd.extend(["export", report])
        elif normalized:
            # Format: task <filter> export
            cmd.extend(tokens)
            cmd.append("export")
        else:
            # Format: task export (export all)
            cmd.append("export")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)

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
        cmd = [
            self.command,
            "rc.confirmation=off",
            "rc.hooks=0",
            f"uuid:{uuid}",
            "modify",
        ]
        for key, value in modifications.items():
            cmd.append(f"{key}:{value}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        return result.returncode == 0
