"""Report/filter modal widget for changing the current TaskWarrior view."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Static
from textual.containers import Vertical


class ReportModal(ModalScreen[str | None]):
    """Modal screen for changing the current filter or report.

    Accepts either:
    - A report name (e.g., "next", "all", "overdue")
    - A filter expression (e.g., "status:pending", "project:work +tag")
    - A combination (e.g., "status:pending next")

    Returns the filter/report string on submit (Enter key),
    or None if cancelled (Escape key).
    """

    def compose(self) -> ComposeResult:
        """Compose the modal with a title and input field."""
        yield Vertical(
            Static("Enter filter or report:", id="report-label"),
            Input(
                id="report-input",
                placeholder="e.g., next, status:pending, project:work all",
            ),
            id="report-modal-container",
        )

    def on_mount(self) -> None:
        """Focus the input field when modal appears."""
        self.query_one("#report-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key - submit the filter/report."""
        self.dismiss(event.value)

    def action_close_modal(self) -> None:
        """Handle Escape key - cancel without changes."""
        self.dismiss(None)

    BINDINGS = [
        ("escape", "close_modal", "Cancel"),
    ]
