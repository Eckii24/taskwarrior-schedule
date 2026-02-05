# Schedule TUI

A terminal-based user interface (TUI) for **quick rescheduling of TaskWarrior tasks via hotkeys**. Speed up your task management workflow by batch-rescheduling multiple tasks with a single keypress.

## Features

- **Visual task list** from any TaskWarrior report (next, all, overdue, or custom filters)
- **Hotkey-based scheduling** - Press 1-9 to instantly reschedule tasks
- **Multi-select capability** - Batch update multiple tasks at once
- **Multiple date field editing** - Modify scheduled, due, and wait dates simultaneously
- **Vim-style navigation** (j/k keys) for keyboard-centric workflow
- **Report switching** - View different task lists on the fly

## Quick Start

Instead of typing `task 42 modify scheduled:tomorrow` repeatedly for 10 tasks, you can:
1. Press **Tab** to select multiple tasks
2. Press **1** to schedule them all to tomorrow
3. All selected tasks are updated instantly

## Installation

### Requirements

- Python >= 3.11
- TaskWarrior >= 2.5 (tested with 3.4.2)

### Install as a Tool (Recommended)

```bash
# Clone repository
git clone <repo-url>
cd taskwarrior-schedule

# Install with uv
uv tool install .

# Run
schedule
```

### Alternative: Install in Development Mode

```bash
# Clone repository
git clone <repo-url>
cd taskwarrior-schedule

# Install editable
uv pip install -e .

# Run
schedule
```

## Keyboard Shortcuts

### Navigation
- **`j`** / **`k`** - Move cursor down/up (vim-style)
- **Arrow keys** - Also work for navigation
- **`q`** - Quit application

### Task Selection
- **`Tab`** - Toggle selection of current task (● marker appears)
- **`Shift+A`** - Select all visible tasks
- Selection automatically clears after batch operations

### Date Field Toggles
- **`w`** - Toggle "wait" date field on/off
- **`s`** - Toggle "scheduled" date field on/off (default: active)
- **`d`** - Toggle "due" date field on/off

Active fields are shown in the info bar. When you press a scheduling hotkey, it modifies ALL active fields for ALL selected tasks.

### Scheduling Hotkeys
- **`0`** - Clear all active date fields (removes dates)
- **`1`** - Schedule to tomorrow (configurable)
- **`2`** - Schedule to +2 days (configurable)
- **`3`** - Schedule to +3 days (configurable)
- **`4`** - Schedule to start of week (configurable)
- **`5`** - Schedule to start of month (configurable)
- **`6-9`** - Available for custom configuration

### Report/Filter Management
- **`r`** - Open report modal to change current TaskWarrior report/filter

## Configuration

### Config File Location

The app looks for configuration in this order:
1. Environment variable: `SCHEDULE_CONFIG_FILE` (full path to YAML file)
2. XDG standard: `~/.config/schedule/config.yaml`
3. Falls back to defaults if file doesn't exist

### Configuration File Format

Create `~/.config/schedule/config.yaml`:

```yaml
# Default report to load on startup
default_report: "next"

# Date fields active by default (scheduled, due, wait)
default_date_fields:
  - scheduled

# Whether to show confirmation before scheduling (not yet implemented)
confirm_before_schedule: false

# Hotkey mappings (1-9 available, customize as needed)
hotkeys:
  "1": "tomorrow"
  "2": "+2d"           # 2 days from now
  "3": "+3d"           # 3 days from now
  "4": "sow"           # Start of week
  "5": "som"           # Start of month
  "6": "eow"           # End of week (example)
  "7": "+1w"           # 1 week from now (example)
  # "8": "custom_date"  # Add your own
  # "9": "custom_date"  # Add your own
```

### Default Configuration

If no config file exists, these defaults apply:

```python
{
    "default_report": "next",
    "default_date_fields": ["scheduled"],
    "confirm_before_schedule": False,
    "hotkeys": {
        "1": "tomorrow",
        "2": "+2d",
        "3": "+3d",
        "4": "sow",
        "5": "som",
    }
}
```

### Environment Variables

- **`SCHEDULE_CONFIG_FILE`** - Override default config path
  ```bash
  SCHEDULE_CONFIG_FILE=/tmp/my-schedule-config.yaml schedule
  ```
- **`XDG_CONFIG_HOME`** - Affects default config directory (defaults to `~/.config`)

### TaskWarrior Date Format Support

Hotkey values can use any TaskWarrior date format:
- **Absolute dates**: `2024-12-25`, `12/25/2024`
- **Relative dates**: `+3d`, `+2w`, `+1m`, `-1d`
- **Named dates**: `tomorrow`, `yesterday`, `today`
- **Week references**: `sow`, `eow`, `monday`, `friday`
- **Month references**: `som`, `eom`

## Usage Examples

### Example 1: Quick Reschedule Single Task

```
1. Launch: schedule
2. Navigate to task with j/k
3. Press s (ensure scheduled field active)
4. Press 1 (schedule to tomorrow)
5. Task updated, list refreshes
```

### Example 2: Batch Schedule Multiple Tasks

```
1. Launch: schedule
2. Navigate to first task
3. Press Tab (select task 1)
4. Press j (move down)
5. Press Tab (select task 2)
6. Press j (move down)
7. Press Tab (select task 3)
8. Press 4 (schedule all to start of week)
9. All 3 tasks updated, selection clears
```

### Example 3: Set Multiple Date Fields

```
1. Launch: schedule
2. Press w (activate wait field)
3. Press d (activate due field)
4. Info bar shows: "Active: due, scheduled, wait"
5. Select tasks with Tab
6. Press 2 (all 3 fields set to +2d)
```

### Example 4: Change Report

```
1. Launch: schedule (shows "next" report)
2. Press r (open report modal)
3. Type: overdue
4. Press Enter
5. Task list reloads with overdue tasks
```

### Example 5: Clear Dates

```
1. Launch: schedule
2. Press Shift+A (select all visible)
3. Press 0 (clear active date fields)
4. All tasks have scheduled dates removed
```

### Example 6: Custom Filter

```
1. Launch: schedule
2. Press r
3. Type: project:work status:pending
4. Press Enter
5. Shows only work project pending tasks
```

### Example 7: Using Environment Config

```bash
# Create custom config
cat > /tmp/work-schedule.yaml <<EOF
default_report: "project:work"
default_date_fields:
  - due
  - scheduled
hotkeys:
  "1": "+1d"
  "2": "+1w"
  "3": "friday"
EOF

# Run with custom config
SCHEDULE_CONFIG_FILE=/tmp/work-schedule.yaml schedule
```

## Advanced Features

### Multi-Select Visual Indicators
Selected tasks show **● marker** in the ID column (e.g., `● 42` instead of `42`). Markers disappear after batch operations complete.

### Date Field Combinations
Active fields are **additive** - you can have multiple active simultaneously:
- Just scheduled: Press `s` (default)
- Scheduled + Due: Press `s`, then `d`
- All three: Press `s`, `d`, `w`
- Toggle off: Press the same key again

### Report/Filter Intelligence
The app automatically detects whether you're using a report or filter:
- `"next"` → Uses "next" report
- `"status:pending"` → Uses filter
- `"project:work next"` → Uses "next" report with "project:work" filter

## Project Structure

```
taskwarrior-schedule/
├── pyproject.toml          # Package configuration
├── README.md               # This file
├── uv.lock                 # Dependency lock file
└── src/
    └── schedule/
        ├── __init__.py         # Package marker (v0.1.0)
        ├── main.py             # Entry point - launches app
        ├── app.py              # Main TUI application
        ├── config.py           # Configuration loading
        ├── taskwarrior.py      # TaskWarrior CLI wrapper
        ├── app.tcss            # Textual CSS stylesheet
        └── widgets/
            ├── __init__.py
            ├── task_table.py   # Task table widget
            └── report_modal.py # Report selection modal
```

## Dependencies

- **textual** >= 0.50.0 - TUI framework
- **pyyaml** >= 6.0 - Config file parsing

## TaskWarrior Integration

The app uses TaskWarrior's CLI interface via subprocess calls:

**Export tasks:**
```bash
task rc.confirmation=off rc.hooks=0 [filter] export [report]
```

**Modify task:**
```bash
task rc.confirmation=off rc.hooks=0 uuid:<uuid> modify field:value
```

Works with any TaskWarrior installation (2.5+) and respects TaskWarrior's date parsing.

## Limitations

- No task creation/deletion (view and reschedule only)
- No undo functionality
- No date validation (delegates to TaskWarrior)
- No persistent selection state across app restarts
- Cursor resets to top after refresh

## License

See LICENSE file for details.

## Contributing

Contributions welcome! Please open an issue or pull request.