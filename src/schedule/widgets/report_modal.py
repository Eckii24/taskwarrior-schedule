"""Report modal widget for displaying task scheduling options."""

from textual.widgets import Modal


class ReportModal(Modal):
    """Modal dialog for scheduling task options."""

    def __init__(self, task_id: int, *args, **kwargs) -> None:
        """Initialize the report modal.

        Args:
            task_id: ID of the task being scheduled
        """
        super().__init__(*args, **kwargs)
        self.task_id = task_id
