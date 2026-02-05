# Learnings - Schedule TUI

This file accumulates conventions, patterns, and design decisions discovered during implementation.

---


## Configuration Module Pattern

### XDG Base Directory Standard
- Used `~/.config/schedule/config.yaml` as default location
- Supports environment override via `SCHEDULE_CONFIG_FILE` env var
- Environment variable takes priority over XDG path

### Error Handling Strategy
- Missing file: Return default config (no crash)
- Invalid YAML: Return default config (graceful degradation)
- Empty file (null YAML): Return default config
- Successful parse: Merge file config over defaults (file overrides)

### Default Configuration Structure
```python
DEFAULT_CONFIG = {
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

### Testing Notes
- All three acceptance scenarios verified
- Required README.md for hatchling build system
- PyYAML dependency available from pyproject.toml

---

## Task 1: Project Setup & Package Structure (Complete)

### Package Structure (src-layout)
```
src/schedule/
├── __init__.py          # Package marker, version="0.1.0"
├── main.py              # Entry point: schedule = "schedule.main:main"
├── app.py               # ScheduleApp (Textual App class)
├── config.py            # Config mgmt with XDG + env override
├── taskwarrior.py       # TaskWarrior CLI wrapper (export/modify)
├── app.tcss             # Textual CSS stylesheet template
└── widgets/
    ├── __init__.py
    ├── task_table.py    # DataTable widget for tasks
    └── report_modal.py  # Modal widget for scheduling
```

### pyproject.toml Key Configuration
- **Build Backend**: hatchling (no additional tools needed)
- **Python Requirement**: >=3.11 (type hints, async patterns)
- **Dependencies**: textual>=0.50.0, pyyaml>=6.0
- **Entry Point**: [project.scripts] section, schedule → schedule.main:main
- **Wheel Config**: packages = ["src/schedule"] (src-layout setup)

### Implementation Notes

#### app.py (ScheduleApp)
- Minimal Textual scaffold with Header/Footer
- BINDINGS: q → quit (standard hotkey)
- compose() yields widgets (currently Header/Footer placeholders)
- Ready for widgets integration in next tasks

#### main.py (Entry Point)
- Clean entry point: creates ScheduleApp(), calls .run()
- No imports at module level except schedule.app (loads on demand)

#### taskwarrior.py Integration Points
- `export(report)`: Runs `task {report} export` → JSON list
- `modify(task_id, changes)`: Runs `task {id} modify key=value`
- Handles subprocess errors gracefully (returns empty/False)
- Compatible with TaskWarrior 2.5+ (standard JSON export)

#### config.py (Pre-existing)
- get_config_path(): XDG standard + env override support
- load_config(): Graceful fallback on errors
- DEFAULT_CONFIG: Includes hotkey mapping for future use

### Verification Results
✅ Directory structure matches spec
✅ pyproject.toml has all required fields
✅ uv pip install -e . succeeds (editable install)
✅ Entry point found: .venv/bin/schedule
✅ from schedule.main import main works
✅ All Python files syntactically valid

### Commit
- **Hash**: 8ab4923
- **Message**: "feat(init): project structure and pyproject.toml"
- **Files**: 14 new (including __pycache__ artifacts)

### Known Issues / Next Steps
- Textual widgets (Header/Footer) are placeholder only
- No error handling for missing TaskWarrior binary yet
- Config merge logic could use unit tests (deferred to later task)
- CSS stylesheet empty placeholder (needs Textual styling knowledge)

---

## Task 4: Date Field Toggle Manager (Complete)

### DateFieldManager Implementation

**Location**: `src/schedule/app.py` (simple, no separate module needed)

**Design**:
- Class manages a set of active date field names
- Fields: "scheduled", "due", "wait"
- Constraint: At least one field must always be active

**Key Methods**:
- `__init__(initial_fields: list[str])`: Initialize with list from config's `default_date_fields`
- `toggle(field: str)`: Add field if not present, remove if present (but never empty set)
- `get_active() -> list[str]`: Return sorted list of active fields

**Toggle Logic**:
```python
if field in self.active:
    if len(self.active) > 1:  # Only remove if more than 1 active
        self.active.discard(field)
else:
    self.active.add(field)  # Always safe to add
```

**Verification Results**:
✅ Initial state with `["scheduled"]` works
✅ Toggle adds fields (scheduled → due, due → wait)
✅ Toggle removes fields when safe
✅ Toggle prevents removal of last field (at least one active constraint)
✅ get_active() returns sorted list for predictable ordering

### Design Decisions

**Why in app.py?** 
- Small, self-contained class (40 lines)
- Used by ScheduleApp widget layer (upcoming tasks)
- No circular imports risk

**Why set not list?**
- O(1) toggle operations
- No duplicate fields possible
- Idiomatic Python for membership testing

**Why sorted in get_active()?**
- Predictable ordering for UI rendering
- Consistent test output

### Integration Points
- Will be instantiated in ScheduleApp with config: `DateFieldManager(config["default_date_fields"])`
- Used by hotkey handlers (Task 5+) to determine which fields to modify
- Example: If both "scheduled" and "due" active, hotkey "1" → set both to tomorrow

### Next Steps (Task 5+)
- Pass DateFieldManager instance to UI widgets
- Hotkeys W/S/D call manager.toggle()
- Display active fields in UI (visual indicator)

---

## Task 3: TaskWarrior Subprocess Wrapper (Complete)

### Implementation: TaskWarriorClient Class

**Key Design Decisions:**
- Used `TaskWarriorClient` class name (not `TaskWarrior` from Task 1 stub) for clarity
- Methods: `get_tasks(report)` and `modify_task(uuid, **modifications)`
- JSON parsing via `subprocess.run(...capture_output=True, text=True)`
- Direct CLI command building: `task export <report>` and `task uuid:<uuid> modify ...`

### Method Details

#### get_tasks(report: str) -> List[Dict[str, Any]]
- Runs: `task export <report>`
- Returns: List of task dicts with ISO-8601 dates as strings (no conversion/parsing)
- Error handling:
  - FileNotFoundError: Raised by subprocess if `task` binary not in PATH
  - subprocess.CalledProcessError: Raised if report is invalid or command fails
  - json.JSONDecodeError: Propagated if JSON parsing fails

#### modify_task(uuid: str, **modifications: Any) -> bool
- Runs: `task uuid:<uuid> modify key:value ... rc.confirmation:off`
- Command format: `["task", f"uuid:{uuid}", "modify", "key:value", ..., "rc.confirmation:off"]`
- Returns: True on success (returncode==0), False on any exception
- Always includes `rc.confirmation:off` to prevent interactive prompts
- Uses kwargs for flexible field modifications

### Implementation Notes

**Command Format Specifics:**
- TW modify uses colons not equals: `scheduled:tomorrow` (not `scheduled=tomorrow`)
- Must disable confirmation: `rc.confirmation:off` flag required
- UUID selector: `uuid:<uuid>` format (not task ID)

**Error Handling Strategy:**
- get_tasks: Explicitly raises exceptions (caller decides handling)
- modify_task: Catches all exceptions, returns bool (fire-and-forget for TUI)
- No caching or async - simple synchronous subprocess wrappers

### Verification Results (All Passed)

**Scenario 1: Get tasks returns parsed JSON**
- Created task with tag +qatest
- get_tasks('next') returned list of dicts
- QA task found in results with 'uuid' field present
- ✅ Status: PASSED

**Scenario 2: Modify task changes date field**
- Created task with tag +qamodifytest
- Extracted UUID from export
- modify_task(uuid, scheduled='tomorrow') returned True
- Verified `scheduled` field was set in exported JSON
- ✅ Status: PASSED

**Scenario 3: Handle TaskWarrior not found**
- Set command to nonexistent binary
- get_tasks() raised FileNotFoundError as expected
- ✅ Status: PASSED

### Commit Info
- **Hash**: 1a5150a
- **Message**: "feat(taskwarrior): subprocess wrapper for TW CLI"
- **Files Changed**: src/schedule/taskwarrior.py (44 insertions, 26 deletions)

### Key Learnings
- TW CLI uses colon notation for field syntax (`:` not `=`)
- "next" report is filtered by due/scheduled dates - unscheduled tasks don't appear
- UUID format in TW: hyphenated hex UUID (e.g., `cf5a94cd-c1fc-4ca2-9e6a-0b33827720b3`)
- Confirmation flag is essential for non-interactive modify commands
- JSON export is robust - handles all task fields with proper types (except dates as strings)

### Blocking Dependencies Met
- Task 1 ✅ Package structure in place
- Task 2 ✅ Config module available (not used directly but infrastructure ready)
- Task 3 ✅ This task - subprocess wrapper complete
- Unblocks: Tasks 5 (TUI widgets), 6 (task loading), 8 (scheduling)

---

## Task 5: UI Core - App Layout with DataTable and Vim Navigation

### DateFieldManager Implementation

**Location**: `src/schedule/config.py` (with other config utilities)

**Design**:
- Simple class managing active date fields for display and modification
- Fields: "scheduled", "due", "wait" (customizable via config)
- No constraint on field counts (can be empty, single, or multiple)
- Used for both UI display (info bar) and action determination

**Key Methods**:
- `__init__(active_fields: list[str] | None = None)`: Initialize with optional field list
- `toggle(field: str)`: Add field if absent, remove if present
- `get_active() -> list[str]`: Return sorted list of active fields for display

**Implementation Notes**:
- Uses set internally for O(1) toggle operations
- get_active() returns sorted list for predictable ordering in UI
- Flexible design allows W/S/D toggles (Task 6) to modify active fields dynamically

### ScheduleApp Class Structure

**Imports**:
```python
from textual.app import ComposeResult, App
from textual.binding import Binding
from textual.widgets import Header, Footer, DataTable, Static
from schedule.config import load_config, DateFieldManager
from schedule.taskwarrior import TaskWarriorClient
```

**Initialization** (`__init__`):
- Loads config via `load_config()` (with defaults fallback)
- Creates TaskWarrior client: `self.tw_client = TaskWarriorClient()`
- Initializes date field manager with config's `default_date_fields`
- Stores current report from config (default: "next")
- Initializes empty tasks list: `self.tasks = []`

**Composition** (`compose()`):
Three-panel layout:
1. `Header()` - Standard Textual header (shows app title/subtitle)
2. `Static(text, id="info-bar")` - Custom info bar with report name and active fields
3. `DataTable(id="task-table", cursor_type="row")` - Main task list
4. `Footer()` - Standard Textual footer (shows bindings)

Info bar format: `f"Report: {self.current_report} | Active: {', '.join(self.date_field_mgr.get_active())}"`

**Key Bindings**:
```python
BINDINGS = [
    Binding("q", "quit", "Quit", show=True),
    Binding("j", "cursor_down", "Down", show=False),  # Vim navigation
    Binding("k", "cursor_up", "Up", show=False),      # Vim navigation
]
```
- j/k hidden from footer (show=False) for cleaner UI
- Arrow keys work automatically via Textual defaults
- q prominently displayed for visibility

### on_mount() Method

**Flow**:
1. Query DataTable widget by ID: `table = self.query_one("#task-table", DataTable)`
2. Add columns in order: ID, Description, Project, Scheduled, Due, Wait
3. Try to load tasks from TaskWarrior via `get_tasks(current_report)`
4. If tasks exist: iterate and add rows with data extraction
5. If empty: show placeholder row to avoid empty table visual
6. On exception: catch and display error message in first row

**Data Extraction**:
```python
row_data = [
    str(task.get("id", idx)),           # Task ID (fallback to row number)
    task.get("description", "")[:50],   # Truncate description to 50 chars
    task.get("project", ""),             # Project name (may be empty)
    task.get("scheduled", "-"),          # Scheduled date or "-"
    task.get("due", "-"),                # Due date or "-"
    task.get("wait", "-"),               # Wait date or "-"
]
```

**Error Handling**:
- Wraps entire on_mount() in try/except
- Catches subprocess.CalledProcessError (bad report name)
- Catches FileNotFoundError (TaskWarrior not installed)
- Catches any Exception (JSON parse errors, etc.)
- Displays error message in single row rather than crashing

### Action Methods

**action_cursor_down()** and **action_cursor_up()**:
- Simple delegation to DataTable's built-in actions
- Allows vim-style j/k bindings to work
- Textual framework handles cursor movement and bounds

### Verification Results

✅ All imports successful (config, taskwarrior, textual modules)
✅ DateFieldManager toggle/get_active() logic verified
✅ App instantiation successful (no init errors)
✅ Compose() yields correct widget sequence: Header → Static → DataTable → Footer
✅ Info bar displays report name and active fields correctly
✅ DataTable structure includes all required columns

### Implementation Decisions

**Why Static widget for info bar?**
- Header widget is styled but doesn't take custom text easily
- Static is lightweight and perfect for simple text display
- Can be updated later if dynamic content needed

**Why truncate description to 50 chars?**
- Terminal width constraints (typical 80-120 cols)
- Keeps table readable without text wrapping
- Future: Make configurable if needed

**Why show "-" for missing date fields?**
- More readable than empty strings
- Consistent with TUI conventions
- Distinguishes "no value" from "empty description"

**Why placeholder row for empty list?**
- Textual DataTable with no rows can appear broken
- Placeholder provides visual feedback (not silent failure)
- User knows: app running, just no matching tasks

### Design Constraints Met

✅ No hotkey actions implemented (Task 6)
✅ No report modal (Task 7)
✅ Basic layout only, no custom styling
✅ Vim navigation (j/k) functional
✅ Three-panel structure matches spec

### Next Task Dependencies

Task 5b (Multi-Select) builds on:
- DataTable widget and cursor positioning
- Task list loading infrastructure
- Selection state management

Task 6 (Hotkey System) builds on:
- DateFieldManager for field selection
- TaskWarriorClient for modifications
- Action methods pattern (cursor_down/up as template)

### Commit Info
- **Hash**: aba825c
- **Message**: "feat(ui): core app layout with DataTable and navigation"
- **Files**: src/schedule/app.py (81 lines), src/schedule/config.py (+57 lines for DateFieldManager)
- **Total Changes**: 93 insertions

### Known Limitations / Future Work
- No async task loading (TW subprocess blocks UI on slow systems)
- No pagination (large task lists may be slow)
- No sorting/filtering UI (configured via report only)
- Error messages truncated to single row display
- Static info bar (not reactive to later toggles until refresh)

---

## Task 5b: Multi-Select System (Complete)

### Selection State Management

**Location**: `src/schedule/app.py` (ScheduleApp class)

**Design**:
- Track selected task UUIDs in a set: `selected_tasks: set[str]`
- Persistent across navigation (set persists as instance variable)
- Uses UUID format for stable references (unchanged by other operations)

**Key Methods**:

#### `action_toggle_selection()`
- Gets current cursor row index from DataTable
- Maps row index to task in self.tasks list
- Extracts UUID from task dictionary
- Toggles UUID in/out of selected_tasks set
- Updates row styling to show selection visually (● marker in ID column)

#### `action_select_all()`
- Iterates through all tasks in self.tasks
- Adds every task UUID to selected_tasks
- Updates row styling for all rows to show selection state

#### `get_selected_tasks() -> list[str]`
- Returns list of selected task UUIDs if any are selected
- Fallback behavior: if no tasks selected, returns current cursor row UUID
- This enables hotkeys to work on single task or multiple selected tasks
- Returns empty list if no tasks available

#### `clear_selection()`
- Clears the selected_tasks set completely
- Updates row styling for all rows to remove visual indicators
- Called after batch operations (hotkey presses on multiple tasks)

#### `_update_row_styling(row_index: int)`
- Private helper to update visual indicator for a specific row
- Uses DataTable.update_cell() to add ● marker when selected
- Removes marker when not selected
- Gracefully handles missing update_cell() method

**Key Bindings**:
```python
Binding("tab", "toggle_selection", "Select", show=False),
Binding("shift+a", "select_all", "All", show=False),
```
- Tab for individual task toggle (vim-style approach)
- Shift+A for "select all visible" (capital A due to Textual binding syntax)

### Visual Indicator Strategy

**Implementation**:
- Used ID column marker (● bullet point) to indicate selected state
- Simple and non-intrusive: row still readable, selection obvious
- Could upgrade to full row highlighting with CSS in future

**Why this approach?**
- Textual DataTable doesn't have built-in multi-select styling
- Marker in first column is visible and doesn't require CSS expertise
- Compatible with existing data layout

### Integration with Hotkey System (Task 6)

**Expected usage flow**:
1. User presses Tab to select individual tasks
2. Or Shift+A to select all visible tasks
3. User presses hotkey (1-9) to schedule selected tasks
4. Task 6 calls `get_selected_tasks()` to get UUIDs
5. Task 6 calls `clear_selection()` after batch operation complete

### Verification Results

✅ App initializes with empty selected_tasks set
✅ Tab binding present and mapped to toggle_selection
✅ Shift+A binding present and mapped to select_all
✅ get_selected_tasks() returns list type
✅ Selection state tracks multiple UUIDs
✅ clear_selection() empties the set
✅ get_selected_tasks() returns all selected when populated
✅ Methods handle missing UI gracefully (try/except)

### Design Decisions

**Why set instead of list?**
- O(1) toggle operations (no iteration needed)
- No duplicates possible
- Idiomatic for membership testing ("is UUID selected?")

**Why return current row if none selected?**
- Enables hotkeys to work seamlessly on single task
- User doesn't need to explicitly select before pressing hotkey
- Consistent with single-task workflow from Task 5

**Why store UUID not row index?**
- Row index can change (with sorting/filtering in future)
- UUID is stable identifier for the task
- Matches TaskWarrior's native identifier system

**Why visual marker in ID column?**
- DataTable.update_cell() is stable API
- ● marker is clear and doesn't break layout
- Simple fallback if update_cell unavailable

### Known Limitations / Future Work
- Selection not persisted between app restarts (by spec)
- No range selection (Shift+click style) - single select only
- No keyboard shortcuts to deselect all (use Tab individually)
- Marker approach doesn't scale well to 1000+ tasks (performance)
- Could upgrade to CSS row styling for better UX

### Blocking Dependencies Met
- Task 5 ✅ DataTable and task list loading
- App instance structure ready for Task 6 (hotkey system)

### Next Task Dependencies
Task 6 (Hotkey System) will:
- Call `get_selected_tasks()` to batch schedule
- Call `clear_selection()` after batch operations
- Enable multi-task scheduling via hotkeys

### Commit Info
- **Hash**: 09f7e9b
- **Message**: "feat(ui): multi-select with Tab and Shift+A"
- **Files Modified**: src/schedule/app.py
- **Lines Added**: ~90 (selection logic + bindings)
