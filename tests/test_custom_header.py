"""Tests for CustomHeader widget."""

import pytest
from textual.app import App, ComposeResult

from schedule.widgets.custom_header import CustomHeader


class TestCustomHeader:
    """Test CustomHeader widget rendering and updates."""

    @pytest.mark.asyncio
    async def test_header_initial_render(self):
        """Should render header with initial filter and active fields."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield CustomHeader(filter_text="next", active_fields="scheduled, due")

        app = TestApp()
        async with app.run_test() as pilot:
            header = app.query_one(CustomHeader)

            # Check that header exists and has correct initial state
            assert header.filter_text == "next"
            assert header.active_fields == "scheduled, due"

            # Check rendered content (use render() to get the text)
            title = app.query_one(".app-title")
            title_text = title.render()
            assert "Schedule" in str(title_text)

            status = app.query_one(".status-line")
            status_text = status.render()
            assert "Filter: next" in str(status_text)
            assert "Active: scheduled, due" in str(status_text)

    @pytest.mark.asyncio
    async def test_header_update_status(self):
        """Should update status line when update_status is called."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield CustomHeader(filter_text="initial", active_fields="none")

        app = TestApp()
        async with app.run_test() as pilot:
            header = app.query_one(CustomHeader)

            # Update the status
            header.update_status("overdue", "due, wait")
            await pilot.pause()

            # Verify internal state updated
            assert header.filter_text == "overdue"
            assert header.active_fields == "due, wait"

            # Verify rendered content updated
            status = app.query_one(".status-line")
            status_text = status.render()
            assert "Filter: overdue" in str(status_text)
            assert "Active: due, wait" in str(status_text)

    @pytest.mark.asyncio
    async def test_header_empty_values(self):
        """Should handle empty filter and active fields."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield CustomHeader(filter_text="", active_fields="")

        app = TestApp()
        async with app.run_test() as pilot:
            header = app.query_one(CustomHeader)

            assert header.filter_text == ""
            assert header.active_fields == ""

            status = app.query_one(".status-line")
            status_text = status.render()
            assert "Filter: " in str(status_text)
            assert "Active: " in str(status_text)

    @pytest.mark.asyncio
    async def test_header_multiple_updates(self):
        """Should handle multiple consecutive updates."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield CustomHeader(filter_text="filter1", active_fields="field1")

        app = TestApp()
        async with app.run_test() as pilot:
            header = app.query_one(CustomHeader)

            # First update
            header.update_status("filter2", "field2")
            await pilot.pause()
            assert header.filter_text == "filter2"

            # Second update
            header.update_status("filter3", "field3")
            await pilot.pause()
            assert header.filter_text == "filter3"
            assert header.active_fields == "field3"

            # Verify final rendered state
            status = app.query_one(".status-line")
            status_text = status.render()
            assert "Filter: filter3" in str(status_text)
            assert "Active: field3" in str(status_text)

    @pytest.mark.asyncio
    async def test_header_default_initialization(self):
        """Should initialize with empty strings if no parameters provided."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield CustomHeader()

        app = TestApp()
        async with app.run_test() as pilot:
            header = app.query_one(CustomHeader)

            assert header.filter_text == ""
            assert header.active_fields == ""
            assert header.sort_mode == "default"
            assert header.date_format == "absolute"

    @pytest.mark.asyncio
    async def test_header_shows_sort_and_date_format(self):
        """Should display sort mode and date format in status line."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield CustomHeader(
                    filter_text="next",
                    active_fields="scheduled",
                    sort_mode="project",
                    date_format="relative",
                )

        app = TestApp()
        async with app.run_test() as pilot:
            header = app.query_one(CustomHeader)

            assert header.sort_mode == "project"
            assert header.date_format == "relative"

            status = app.query_one(".status-line")
            status_text = status.render()
            assert "Sort: project" in str(status_text)
            assert "Date: relative" in str(status_text)

    @pytest.mark.asyncio
    async def test_header_update_status_with_sort_and_date(self):
        """Should update sort mode and date format via update_status."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield CustomHeader(filter_text="next", active_fields="scheduled")

        app = TestApp()
        async with app.run_test() as pilot:
            header = app.query_one(CustomHeader)

            header.update_status(
                "overdue", "due", sort_mode="due", date_format="relative"
            )
            await pilot.pause()

            assert header.sort_mode == "due"
            assert header.date_format == "relative"

            status = app.query_one(".status-line")
            status_text = status.render()
            assert "Sort: due" in str(status_text)
            assert "Date: relative" in str(status_text)
            assert "Filter: overdue" in str(status_text)
