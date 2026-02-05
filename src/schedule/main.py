"""Main entry point for the schedule application."""

from schedule.app import ScheduleApp


def main() -> None:
    """Run the schedule TUI application."""
    app = ScheduleApp()
    app.run()


if __name__ == "__main__":
    main()
