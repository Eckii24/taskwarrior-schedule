"""Tests for ReportModal widget."""

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Input

from schedule.widgets.report_modal import ReportModal


class TestReportModal:
    """Test ReportModal screen functionality."""

    @pytest.mark.asyncio
    async def test_modal_renders_input(self):
        """Should render modal with input field."""

        class TestApp(App):
            def on_mount(self) -> None:
                self.push_screen(ReportModal())

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            modal_screen = app.screen_stack[-1]
            input_field = modal_screen.query_one("#report-input", Input)
            assert input_field is not None
            assert (
                input_field.placeholder
                == "e.g., next, status:pending, project:work all"
            )

    @pytest.mark.asyncio
    async def test_modal_input_focused_on_mount(self):
        """Should focus input field when modal appears."""

        class TestApp(App):
            def on_mount(self) -> None:
                self.push_screen(ReportModal())

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            modal_screen = app.screen_stack[-1]
            input_field = modal_screen.query_one("#report-input", Input)
            assert input_field.has_focus

    @pytest.mark.asyncio
    async def test_modal_submit_returns_value(self):
        """Should return input value when Enter is pressed."""

        result_holder = {"value": None}

        class TestApp(App):
            def on_mount(self) -> None:
                def callback(result):
                    result_holder["value"] = result

                self.push_screen(ReportModal(), callback=callback)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            modal_screen = app.screen_stack[-1]

            # Type into input
            input_field = modal_screen.query_one("#report-input", Input)
            input_field.value = "project:work next"

            # Submit with Enter
            await pilot.press("enter")
            await pilot.pause()

            # Check callback received correct value
            assert result_holder["value"] == "project:work next"

    @pytest.mark.asyncio
    async def test_modal_escape_returns_none(self):
        """Should return None when Escape is pressed."""

        result_holder = {"value": "not_set"}

        class TestApp(App):
            def on_mount(self) -> None:
                def callback(result):
                    result_holder["value"] = result

                self.push_screen(ReportModal(), callback=callback)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            modal_screen = app.screen_stack[-1]

            # Type something but cancel with Escape
            input_field = modal_screen.query_one("#report-input", Input)
            input_field.value = "should_not_be_returned"

            await pilot.press("escape")
            await pilot.pause()

            # Should return None
            assert result_holder["value"] is None

    @pytest.mark.asyncio
    async def test_modal_empty_submit(self):
        """Should return empty string if submitted with no input."""

        result_holder = {"value": None}

        class TestApp(App):
            def on_mount(self) -> None:
                def callback(result):
                    result_holder["value"] = result

                self.push_screen(ReportModal(), callback=callback)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Submit without typing anything
            await pilot.press("enter")
            await pilot.pause()

            assert result_holder["value"] == ""

    @pytest.mark.asyncio
    async def test_modal_typing_interaction(self):
        """Should handle typing into input field."""

        class TestApp(App):
            def on_mount(self) -> None:
                self.push_screen(ReportModal())

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            modal_screen = app.screen_stack[-1]
            input_field = modal_screen.query_one("#report-input", Input)

            # Simulate typing
            input_field.value = "overdue"
            await pilot.pause()

            assert input_field.value == "overdue"

    @pytest.mark.asyncio
    async def test_modal_multiple_inputs(self):
        """Should handle complex filter expressions."""

        result_holder = {"value": None}

        class TestApp(App):
            def on_mount(self) -> None:
                def callback(result):
                    result_holder["value"] = result

                self.push_screen(ReportModal(), callback=callback)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            modal_screen = app.screen_stack[-1]

            # Complex filter
            complex_filter = "project:work +urgent status:pending all"
            input_field = modal_screen.query_one("#report-input", Input)
            input_field.value = complex_filter

            await pilot.press("enter")
            await pilot.pause()

            assert result_holder["value"] == complex_filter
