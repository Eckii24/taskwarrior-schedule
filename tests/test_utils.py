"""Additional integration and utility tests for ScheduleApp."""

from datetime import datetime, date, timedelta
from unittest.mock import patch

import pytest

from schedule.app import format_date, _format_relative


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

    def test_format_date_relative_mode(self):
        """Should return relative string when relative=True."""
        tomorrow = date.today() + timedelta(days=1)
        date_str = tomorrow.strftime("%Y%m%d") + "T000000Z"
        result = format_date(date_str, relative=True)
        assert result == "tomorrow"

    def test_format_date_relative_dash(self):
        """Should return dash for empty input even in relative mode."""
        assert format_date("-", relative=True) == "-"
        assert format_date("", relative=True) == "-"

    def test_format_date_absolute_is_default(self):
        """Should use absolute format by default (backward compatible)."""
        result = format_date("20260206T120000Z")
        assert "06-02-2026" in result


class TestFormatRelative:
    """Test the _format_relative helper function."""

    def _make_dt(self, days_offset: int) -> datetime:
        target = date.today() + timedelta(days=days_offset)
        return datetime.combine(target, datetime.min.time())

    def test_today(self):
        assert _format_relative(self._make_dt(0)) == "today"

    def test_tomorrow(self):
        assert _format_relative(self._make_dt(1)) == "tomorrow"

    def test_yesterday(self):
        assert _format_relative(self._make_dt(-1)) == "yesterday"

    def test_future_days(self):
        result = _format_relative(self._make_dt(3))
        assert result == "in 3 days"

    def test_past_days(self):
        result = _format_relative(self._make_dt(-5))
        assert result == "5 days ago"

    def test_future_weeks(self):
        result = _format_relative(self._make_dt(14))
        assert "week" in result
        assert result.startswith("in ")

    def test_future_months(self):
        result = _format_relative(self._make_dt(60))
        assert "month" in result
        assert result.startswith("in ")

    def test_past_months(self):
        result = _format_relative(self._make_dt(-90))
        assert "month" in result
        assert result.endswith(" ago")

    def test_future_year(self):
        result = _format_relative(self._make_dt(400))
        assert "year" in result
        assert result.startswith("in ")


class TestScheduleAppBindings:
    """Test application key bindings are properly configured."""

    @pytest.mark.asyncio
    async def test_app_has_required_bindings(self):
        """Should have all required key bindings configured."""
        from schedule.app import ScheduleApp

        app = ScheduleApp()

        binding_keys = [binding.key for _, binding in app._bindings]

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
        assert "o" in binding_keys
        assert "t" in binding_keys
        assert "x" in binding_keys
        assert "m" in binding_keys

    @pytest.mark.asyncio
    async def test_tab_binding_has_priority(self):
        """Tab binding must have priority=True to override Textual focus cycling."""
        from schedule.app import ScheduleApp

        app = ScheduleApp()

        for _, binding in app._bindings:
            if binding.key == "tab":
                assert binding.priority is True
                break
        else:
            pytest.fail("No tab binding found")
