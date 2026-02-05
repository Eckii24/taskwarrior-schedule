"""Report modal widget for changing the current TaskWarrior report."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Static
from textual.containers import Vertical


class ReportModal(ModalScreen[str | None]):
    """Modal screen for changing the current report.
    
    Returns the new report name on submit (Enter key),
    or None if cancelled (Escape key).
    """

    def compose(self) -> ComposeResult:
        """Compose the modal with a title and input field."""
        yield Vertical(
            Static("Enter report name:", id="report-label"),
            Input(id="report-input", placeholder="e.g., next, all, overdue"),
            id="report-modal-container",
        )

    def on_mount(self) -> None:
        """Focus the input field when modal appears."""
        self.query_one("#report-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key - submit the report name."""
        self.dismiss(event.value)

    def action_close_modal(self) -> None:
        """Handle Escape key - cancel without changes."""
        self.dismiss(None)

    BINDINGS = [
        ("escape", "close_modal", "Cancel"),
    ]
