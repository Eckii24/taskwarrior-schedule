"""Task table widget for displaying TaskWarrior tasks."""

from textual.widgets import DataTable


class TaskTable(DataTable):
    """Widget for displaying tasks in a table."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the task table."""
        super().__init__(*args, **kwargs)
        self.add_columns("ID", "Description", "Due", "Priority")
