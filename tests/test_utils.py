"""Additional integration and utility tests for ScheduleApp."""

import pytest

from schedule.app import format_date


class TestHelperFunctions:
    """Test utility helper functions."""

    def test_format_date_with_valid_date(self):
        """Should format valid ISO date to readable format."""
        result = format_date("20260206T120000Z")
        assert "06-02-2026" in result or "Fri" in result

    def test_format_date_with_dash(self):
        """Should return dash for empty/dash input."""
        assert format_date("-") == "-"
        assert format_date("") == "-"

    def test_format_date_with_invalid_date(self):
        """Should return original string for invalid dates."""
        invalid = "not-a-date"
        result = format_date(invalid)
        assert result == invalid


class TestScheduleAppBindings:
    """Test application key bindings are properly configured."""

    @pytest.mark.asyncio
    async def test_app_has_required_bindings(self):
        """Should have all required key bindings configured."""
        from schedule.app import ScheduleApp

        app = ScheduleApp()

        # Get all binding keys
        binding_keys = [binding.key for _, binding in app._bindings]

        # Check essential bindings exist
        assert "j" in binding_keys
        assert "k" in binding_keys
        assert "tab" in binding_keys
        assert "shift+a" in binding_keys
        assert "s" in binding_keys
        assert "d" in binding_keys
        assert "w" in binding_keys
        assert "0" in binding_keys
        assert "1" in binding_keys
        assert "r" in binding_keys
        assert "q" in binding_keys
