# Schedule TUI - TaskWarrior Scheduling Terminal UI

## TL;DR

> **Quick Summary**: Terminal UI App "schedule" für schnelles Reschedulen von TaskWarrior Tasks via Hotkeys (1-9). Ermöglicht Batch-Editing von scheduled/due/wait Feldern mit konfigurierbaren Shortcuts.
> 
> **Deliverables**:
> - Installierbare Python CLI App via `uv tool install`
> - YAML-basierte Konfiguration mit XDG-Standard
> - Textual-basierte TUI mit Header/List/Footer Layout
> 
> **Estimated Effort**: Medium (8-12 Tasks)
> **Parallel Execution**: YES - 3 Waves
> **Critical Path**: Task 1 (Project Setup) → Task 3 (TW Wrapper) → Task 5 (UI Core) → Task 8 (Integration)

---

## Context

### Original Request
Eine Terminal UI App für TaskWarrior, die:
- Tasks aus einem konfigurierbaren Report anzeigt
- Schnelles Reschedulen via Hotkeys 1-9 ermöglicht
- Mehrere Datumsfelder (W/S/D) gleichzeitig bearbeiten kann
- Mit Vim-Navigation (j/k) bedienbar ist
- **Multi-Select via Tab** für Batch-Scheduling auf mehrere Tasks gleichzeitig

### Interview Summary
**Key Discussions**:
- Config: YAML mit XDG-Standard (`~/.config/schedule/config.yaml`) + ENV Override
- TaskWarrior: Direkter subprocess-Aufruf, kein tasklib
- UI: Header mit aktiven Date-Fields als Chips, Footer mit Shortcuts
- Toggle-Verhalten: Additiv (mehrere Date-Fields gleichzeitig aktiv)
- Nach Scheduling: Auto-Refresh der Liste
- Fehler: Non-blocking Toast Notifications
- Navigation: j/k + Arrow Keys, q zum Beenden
- Kein Confirmation-Dialog per Default (aber konfigurierbar)
- **Multi-Select**: Tab zum Markieren, Shift+A für alle, Hotkeys wirken auf alle markierten
- **Nach Batch-Aktion**: Automatische Deselektierung

**Research Findings**:
- TaskWarrior CLI: `task export <report>` für JSON, `task uuid:<uuid> modify scheduled:<value>`
- Date Synonyme: `tomorrow`, `+3d`, `sow`, `som` direkt verwendbar
- Textual: DataTable mit `cursor_type="row"`, ModalScreen für Popups
- Pattern: Dooit/Posting Apps zeigen vim-style Navigation

### Metis Review
**Identified Gaps** (addressed):
- UUID vs ID: Use UUID for stable references after scheduling
- Subprocess blocking: Use async workers for TW calls
- Date clearing: Added 0-Taste zum Löschen von Datumsfeldern
- Column order: ID, Description, Project, Scheduled, Due, Wait

---

## Work Objectives

### Core Objective
Eine fokussierte TUI-Anwendung, die das repetitive Reschedulen von TaskWarrior Tasks durch Hotkeys drastisch beschleunigt.

### Concrete Deliverables
- `src/schedule/` Python Package mit Layered Architecture
- `pyproject.toml` für `uv tool install schedule`
- CLI Entry Point `schedule` startet die TUI
- Config File Support: `~/.config/schedule/config.yaml`

### Definition of Done
- [x] `uv tool install .` installiert das Tool erfolgreich
- [x] `schedule` startet die TUI ohne Fehler
- [x] Tasks werden aus dem konfigurierten Report geladen
- [x] Hotkeys 1-9 und 0 modifizieren Tasks korrekt
- [x] W/S/D Toggles funktionieren additiv
- [x] R öffnet Report-Änderung Popup
- [x] Tab markiert/demarkiert Tasks für Batch-Operationen
- [x] Shift+A markiert alle sichtbaren Tasks
- [x] Hotkeys 1-9, 0 wirken auf alle markierten Tasks
- [x] Nach Batch-Operation werden Tasks automatisch deselektiert

### Must Have
- Hotkeys 1-9 für Scheduling + 0 für Clear
- W/S/D Toggles für Date-Field Auswahl
- Vim Navigation (j/k) + Arrow Keys
- YAML Config mit Defaults
- TaskWarrior subprocess Integration
- Header/List/Footer Layout
- **Multi-Select via Tab** (Einzelauswahl toggle)
- **Shift+A für "Alle markieren"**
- **Hotkeys wirken auf ALLE markierten Tasks**
- **Auto-Deselect nach Batch-Aktion**

### Must NOT Have (Guardrails)
- **KEINE** Task-Erstellung oder Löschung
- **KEINE** Task-Filterung über Report hinaus
- **KEINE** Bearbeitung von Description/Project/Tags
- **KEINE** Custom Themes oder Farbschemata
- **KEINE** Undo-Funktionalität
- **KEINE** Help-Screens über Footer hinaus
- **KEINE** Logging/Debug-Modi
- **KEINE** Custom Date-Berechnungen (Werte direkt an TW durchreichen)
- **KEINE** automatisierten Tests (explizit out of scope)

---

## Verification Strategy

> **UNIVERSAL RULE: ZERO HUMAN INTERVENTION**
>
> ALL tasks in this plan MUST be verifiable WITHOUT any human action.
> This is NOT conditional — it applies to EVERY task, regardless of test strategy.

### Test Decision
- **Infrastructure exists**: NO (new project)
- **Automated tests**: None (per user decision)
- **Framework**: None

### Agent-Executed QA Scenarios (MANDATORY — ALL tasks)

> These describe how the executing agent DIRECTLY verifies the deliverable
> by running it — using interactive_bash for TUI testing, subprocess for CLI verification.

**Verification Tool by Deliverable Type:**

| Type | Tool | How Agent Verifies |
|------|------|-------------------|
| **TUI/CLI** | interactive_bash (tmux) | Run command, send keystrokes, validate output |
| **Config Loading** | Bash | Create config, run app, verify behavior |
| **Package Install** | Bash | `uv tool install .`, verify entry point exists |

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: Project Setup (pyproject.toml, structure)
└── Task 2: Config Module (YAML loading, defaults)

Wave 2 (After Wave 1):
├── Task 3: TaskWarrior Wrapper (subprocess, JSON parsing)
├── Task 4: Date Field Manager (toggle logic)
├── Task 5: UI Core (App, Layout, DataTable)
└── Task 5b: Multi-Select System (Tab, Shift+A, selection state)

Wave 3 (After Wave 2):
├── Task 6: Hotkey System (1-9, 0, W/S/D, R, q + batch support)
├── Task 7: Report Popup (ModalScreen)
└── Task 8: Integration & Polish

Critical Path: Task 1 → Task 3 → Task 5 → Task 5b → Task 6 → Task 8
Parallel Speedup: ~40% faster than sequential
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 2,3,4,5,5b,6,7,8 | 2 |
| 2 | 1 | 5,6,8 | 3,4 |
| 3 | 1 | 5,6,8 | 2,4 |
| 4 | 1 | 6,8 | 2,3 |
| 5 | 2,3 | 5b,6,7,8 | 4 |
| 5b | 5 | 6,8 | 7 |
| 6 | 4,5,5b | 8 | 7 |
| 7 | 5 | 8 | 5b,6 |
| 8 | 6,7 | None | None (final) |

### Agent Dispatch Summary

| Wave | Tasks | Recommended Approach |
|------|-------|---------------------|
| 1 | 1, 2 | Run in parallel - independent foundation |
| 2 | 3, 4, 5, 5b | Run in parallel - Task 5b after 5 |
| 3 | 6, 7, 8 | Run 6+7 parallel, then 8 as final integration |

---

## TODOs

- [x] 1. Project Setup & Package Structure

  **What to do**:
  - Create `pyproject.toml` with hatchling build backend
  - Set Python 3.11+ requirement
  - Add dependencies: `textual>=0.50.0`, `pyyaml>=6.0`
  - Configure `[project.scripts]` entry point: `schedule = "schedule.main:main"`
  - Create directory structure:
    ```
    src/
    └── schedule/
        ├── __init__.py
        ├── main.py          # Entry point
        ├── app.py           # Textual App class
        ├── config.py        # Config loading
        ├── taskwarrior.py   # TW subprocess wrapper
        ├── widgets/
        │   ├── __init__.py
        │   ├── task_table.py
        │   └── report_modal.py
        └── app.tcss         # Styles
    ```

  **Must NOT do**:
  - Don't add test dependencies
  - Don't create elaborate package metadata
  - Don't add optional dependencies

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standard boilerplate, well-defined structure
  - **Skills**: [`git-master`]
    - `git-master`: Initial commit nach Setup

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: All other tasks
  - **Blocked By**: None (can start immediately)

  **References**:
  - **External**: UV Tool Installation: https://docs.astral.sh/uv/guides/tools/
  - **External**: Hatchling Build Backend: https://hatch.pypa.io/latest/config/build/

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: Project structure created correctly
    Tool: Bash
    Preconditions: Empty git repo
    Steps:
      1. ls -la src/schedule/
      2. Assert: __init__.py exists
      3. Assert: main.py exists
      4. Assert: app.py exists
      5. Assert: config.py exists
      6. Assert: taskwarrior.py exists
      7. Assert: widgets/ directory exists
      8. cat pyproject.toml
      9. Assert: [project.scripts] contains "schedule"
      10. Assert: requires-python = ">=3.11"
    Expected Result: All files and structure present
    Evidence: Terminal output captured

  Scenario: Package is installable
    Tool: Bash
    Preconditions: pyproject.toml exists
    Steps:
      1. uv pip install -e .
      2. Assert: Exit code 0
      3. which schedule || uv run which schedule
      4. Assert: schedule entry point found
    Expected Result: Package installs without errors
    Evidence: Installation output captured
  ```

  **Commit**: YES
  - Message: `feat(init): project structure and pyproject.toml`
  - Files: `pyproject.toml`, `src/schedule/**`
  - Pre-commit: `uv pip install -e .`

---

- [x] 2. Configuration Module

  **What to do**:
  - Create `config.py` with Config dataclass/class
  - Implement YAML loading from XDG path (`~/.config/schedule/config.yaml`)
  - Check `SCHEDULE_CONFIG_FILE` env var first
  - Define defaults:
    ```python
    DEFAULT_CONFIG = {
        "default_report": "next",
        "default_date_fields": ["scheduled"],  # Active at startup
        "confirm_before_schedule": False,
        "hotkeys": {
            "1": "tomorrow",
            "2": "+2d",
            "3": "+3d",
            "4": "sow",
            "5": "som",
            # 6-9 undefined by default
        }
    }
    ```
  - Return merged config (file overrides defaults)
  - Handle missing file gracefully (use defaults)
  - Handle invalid YAML (use defaults, could log warning)

  **Must NOT do**:
  - Don't create config file automatically
  - Don't add validation beyond basic type checks
  - Don't add config write functionality

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple data loading, well-defined schema
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Tasks 5, 6, 8
  - **Blocked By**: Task 1 (needs package structure)

  **References**:
  - **External**: PyYAML docs: https://pyyaml.org/wiki/PyYAMLDocumentation
  - **External**: XDG Base Directory: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: Config loads defaults when no file exists
    Tool: Bash
    Preconditions: No config file at ~/.config/schedule/config.yaml
    Steps:
      1. rm -f ~/.config/schedule/config.yaml
      2. uv run python -c "from schedule.config import load_config; c = load_config(); print(c)"
      3. Assert: output contains "default_report"
      4. Assert: output contains "next" (default report)
      5. Assert: output contains "scheduled" (default date field)
    Expected Result: Defaults are returned
    Evidence: Python output captured

  Scenario: Config loads from custom path via ENV
    Tool: Bash
    Preconditions: None
    Steps:
      1. echo "default_report: custom_report" > /tmp/test-schedule-config.yaml
      2. SCHEDULE_CONFIG_FILE=/tmp/test-schedule-config.yaml uv run python -c "from schedule.config import load_config; c = load_config(); print(c['default_report'])"
      3. Assert: output is "custom_report"
      4. rm /tmp/test-schedule-config.yaml
    Expected Result: ENV var overrides default path
    Evidence: Python output captured

  Scenario: Invalid YAML uses defaults
    Tool: Bash
    Preconditions: None
    Steps:
      1. echo "invalid: yaml: [" > /tmp/bad-config.yaml
      2. SCHEDULE_CONFIG_FILE=/tmp/bad-config.yaml uv run python -c "from schedule.config import load_config; c = load_config(); print(c['default_report'])"
      3. Assert: output is "next" (default, not crash)
      4. rm /tmp/bad-config.yaml
    Expected Result: Graceful fallback to defaults
    Evidence: Python output captured
  ```

  **Commit**: YES
  - Message: `feat(config): YAML config loading with XDG support`
  - Files: `src/schedule/config.py`
  - Pre-commit: `uv run python -c "from schedule.config import load_config; load_config()"`

---

- [x] 3. TaskWarrior Subprocess Wrapper

  **What to do**:
  - Create `taskwarrior.py` with `TaskWarriorClient` class
  - Implement methods:
    ```python
    def get_tasks(self, report: str) -> list[dict]:
        """Run 'task export <report>' and parse JSON"""
    
    def modify_task(self, uuid: str, **modifications) -> bool:
        """Run 'task uuid:<uuid> modify key:value ...'"""
    ```
  - Use `subprocess.run` with `capture_output=True, text=True`
  - Parse JSON from export (ISO-8601 dates as strings - no conversion!)
  - Handle errors: TaskWarrior not found, invalid report, modify failures
  - Add `rc.confirmation:off` to modify commands (non-interactive)

  **Must NOT do**:
  - Don't parse formatted table output (only JSON)
  - Don't convert dates (pass through as-is from TW)
  - Don't cache tasks locally
  - Don't batch modifications

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple subprocess wrapper, well-defined interface
  - **Skills**: []
    - No special skills needed

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 2, 4)
  - **Blocks**: Tasks 5, 6, 8
  - **Blocked By**: Task 1 (needs package structure)

  **References**:
  - **External**: TaskWarrior Export: https://taskwarrior.org/docs/commands/export/
  - **External**: TaskWarrior Modify: https://taskwarrior.org/docs/commands/modify/
  - **External**: TW Date Synonyms: https://taskwarrior.org/docs/dates/

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: Get tasks returns parsed JSON
    Tool: Bash
    Preconditions: TaskWarrior installed, at least one pending task exists
    Steps:
      1. task add "QA Test Task for Schedule" project:QATest +qatest
      2. uv run python -c "
         from schedule.taskwarrior import TaskWarriorClient
         tw = TaskWarriorClient()
         tasks = tw.get_tasks('next')
         print(f'Got {len(tasks)} tasks')
         qa_tasks = [t for t in tasks if 'qatest' in t.get('tags', [])]
         print(f'Found QA task: {len(qa_tasks) > 0}')
         if qa_tasks:
             print(f'Has uuid: {\"uuid\" in qa_tasks[0]}')"
      3. Assert: "Got" followed by a number > 0
      4. Assert: "Found QA task: True"
      5. Assert: "Has uuid: True"
      6. task +qatest delete rc.confirmation:off
    Expected Result: Tasks parsed with UUID
    Evidence: Python output captured

  Scenario: Modify task changes date field
    Tool: Bash
    Preconditions: TaskWarrior installed
    Steps:
      1. task add "Modify Test Task" project:QATest +qamodifytest
      2. UUID=$(task +qamodifytest export | uv run python -c "import sys,json; print(json.load(sys.stdin)[0]['uuid'])")
      3. uv run python -c "
         from schedule.taskwarrior import TaskWarriorClient
         tw = TaskWarriorClient()
         result = tw.modify_task('$UUID', scheduled='tomorrow')
         print(f'Success: {result}')"
      4. Assert: "Success: True"
      5. task +qamodifytest export | grep -q "scheduled"
      6. Assert: Exit code 0 (scheduled field exists)
      7. task +qamodifytest delete rc.confirmation:off
    Expected Result: Task modified successfully
    Evidence: Command outputs captured

  Scenario: Handle TaskWarrior not found
    Tool: Bash
    Preconditions: None
    Steps:
      1. PATH="" uv run python -c "
         from schedule.taskwarrior import TaskWarriorClient
         tw = TaskWarriorClient()
         try:
             tw.get_tasks('next')
             print('No error')
         except Exception as e:
             print(f'Error: {type(e).__name__}')" 2>&1
      2. Assert: output contains "Error:" (exception raised)
    Expected Result: Graceful error handling
    Evidence: Python output captured
  ```

  **Commit**: YES
  - Message: `feat(taskwarrior): subprocess wrapper for TW CLI`
  - Files: `src/schedule/taskwarrior.py`
  - Pre-commit: `uv run python -c "from schedule.taskwarrior import TaskWarriorClient"`

---

- [x] 4. Date Field Toggle Manager

  **What to do**:
  - Create simple state management for active date fields
  - Can be in `app.py` or separate small module
  - Track which fields are active: `{"scheduled", "due", "wait"}`
  - Implement toggle logic (add if not present, remove if present)
  - At least one field must always be active (prevent empty selection)
  - Load initial state from config `default_date_fields`

  **Must NOT do**:
  - Don't create elaborate state management
  - Don't persist toggle state (resets on app restart)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple set operations, minimal code
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 2, 3)
  - **Blocks**: Tasks 6, 8
  - **Blocked By**: Task 1 (needs package structure)

  **References**:
  - **Pattern**: Python set operations for toggle logic

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: Toggle adds and removes fields
    Tool: Bash
    Preconditions: Package installed
    Steps:
      1. uv run python -c "
         from schedule.app import DateFieldManager  # or wherever it lives
         mgr = DateFieldManager(['scheduled'])
         print(f'Initial: {mgr.active}')
         mgr.toggle('due')
         print(f'After toggle due: {mgr.active}')
         mgr.toggle('scheduled')
         print(f'After toggle scheduled: {mgr.active}')
         mgr.toggle('due')
         print(f'After toggle due again: {mgr.active}')"
      2. Assert: Initial contains "scheduled"
      3. Assert: After toggle due contains both "scheduled" and "due"
      4. Assert: After toggle scheduled contains only "due"
      5. Assert: After toggle due again shows fallback (at least one active)
    Expected Result: Toggle logic works correctly
    Evidence: Python output captured
  ```

  **Commit**: YES (groups with Task 5)
  - Message: `feat(app): date field toggle manager`
  - Files: `src/schedule/app.py` (or dedicated module)

---

- [x] 5. UI Core: App, Layout, DataTable

  **What to do**:
  - Create Textual `App` class in `app.py`
  - Implement three-panel layout:
    ```
    ┌─────────────────────────────────────┐
    │ schedule │ Report: next │ [S] [D]   │  ← Header
    ├─────────────────────────────────────┤
    │ ID │ Description │ Project │ Sched  │  ← DataTable
    │  1 │ Task one    │ Work    │ tmrw   │
    │  2 │ Task two    │ Home    │ -      │
    ├─────────────────────────────────────┤
    │ W S D │ R │ 1:tmrw 2:+2d 3:+3d ... │  ← Footer
    └─────────────────────────────────────┘
    ```
  - Use `Header` widget (custom) for app name + report + active fields as chips
  - Use `DataTable` with `cursor_type="row"` for task list
  - Use `Footer` for shortcuts display
  - Columns: ID, Description, Project, Scheduled, Due, Wait
  - Bind vim keys: `j`/`k` for navigation (alongside arrows)
  - Load tasks from TaskWarriorClient on mount
  - Display placeholder when list is empty

  **Must NOT do**:
  - Don't add custom styling beyond basic layout
  - Don't implement hotkey actions (Task 6)
  - Don't implement report modal (Task 7)

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UI layout, widget composition, visual structure
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES (late start in Wave 2)
  - **Parallel Group**: Wave 2 (starts after 2+3 complete)
  - **Blocks**: Tasks 6, 7, 8
  - **Blocked By**: Tasks 2, 3 (needs config and TW wrapper)

  **References**:
  - **External**: Textual DataTable: https://textual.textualize.io/widgets/data_table/
  - **External**: Textual Layout Guide: https://textual.textualize.io/how-to/design-a-layout/
  - **Pattern**: Posting app header: https://github.com/darrenburns/posting/blob/main/src/posting/app.py

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: App starts and shows layout
    Tool: interactive_bash (tmux)
    Preconditions: Package installed, TaskWarrior has tasks
    Steps:
      1. tmux new-session -d -s schedule-test "uv run schedule"
      2. sleep 2
      3. tmux capture-pane -t schedule-test -p > /tmp/schedule-output.txt
      4. cat /tmp/schedule-output.txt
      5. Assert: output contains "schedule" (app name in header)
      6. Assert: output contains "Report:" or current report name
      7. Assert: output contains column headers (ID, Description, etc.)
      8. tmux send-keys -t schedule-test "q"
      9. sleep 1
      10. tmux kill-session -t schedule-test 2>/dev/null || true
    Expected Result: TUI displays with correct layout
    Evidence: Screenshot saved to /tmp/schedule-output.txt

  Scenario: Vim navigation works
    Tool: interactive_bash (tmux)
    Preconditions: Package installed, TaskWarrior has at least 2 tasks
    Steps:
      1. tmux new-session -d -s schedule-nav "uv run schedule"
      2. sleep 2
      3. tmux send-keys -t schedule-nav "j"
      4. sleep 0.5
      5. tmux send-keys -t schedule-nav "k"
      6. sleep 0.5
      7. tmux capture-pane -t schedule-nav -p
      8. Assert: No error messages visible
      9. tmux send-keys -t schedule-nav "q"
      10. tmux kill-session -t schedule-nav 2>/dev/null || true
    Expected Result: j/k navigation doesn't crash
    Evidence: Terminal output captured

  Scenario: Empty list shows placeholder
    Tool: interactive_bash (tmux)
    Preconditions: Package installed
    Steps:
      1. Create empty report or use filter that returns no tasks
      2. SCHEDULE_CONFIG_FILE=/tmp/empty-report-config.yaml uv run schedule
         (with config: default_report: "+nonexistenttag")
      3. Capture output
      4. Assert: Shows placeholder text (not crash, not empty screen)
    Expected Result: Graceful empty state
    Evidence: Terminal output captured
  ```

  **Commit**: YES
  - Message: `feat(ui): core app layout with DataTable and navigation`
  - Files: `src/schedule/app.py`, `src/schedule/widgets/task_table.py`, `src/schedule/app.tcss`
  - Pre-commit: `uv run schedule &; sleep 2; kill %1`

---

- [x] 5b. Multi-Select System

  **What to do**:
  - Implement task selection state management
  - Track selected task UUIDs in a set: `selected_tasks: set[str]`
  - Implement key bindings:
    ```python
    ("tab", "toggle_selection", "Select"),
    ("A", "select_all", "All"),  # Shift+A = capital A
    ```
  - Visual indicator for selected rows (highlight/marker)
  - `toggle_selection`: Add/remove current cursor row from selection
  - `select_all`: Add all visible tasks to selection
  - Method `get_selected_tasks() -> list[str]`: Returns UUIDs of selected tasks (or current if none selected)
  - After batch operation: clear selection (`selected_tasks.clear()`)

  **Must NOT do**:
  - Don't persist selection state
  - Don't add complex selection modes (range select, etc.)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple state management with visual feedback
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (after Task 5)
  - **Blocks**: Task 6, 8
  - **Blocked By**: Task 5 (needs DataTable)

  **References**:
  - **External**: Textual DataTable styling: https://textual.textualize.io/widgets/data_table/#styling
  - **Pattern**: Row highlighting via CSS classes or rich text

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: Tab toggles selection on current row
    Tool: interactive_bash (tmux)
    Preconditions: Package installed, at least 2 tasks exist
    Steps:
      1. task add "Select Test 1" +selecttest
      2. task add "Select Test 2" +selecttest
      3. tmux new-session -d -s schedule-select "uv run schedule"
      4. sleep 2
      5. tmux send-keys -t schedule-select "Tab"  # Select first
      6. sleep 0.3
      7. tmux capture-pane -t schedule-select -p > /tmp/select-1.txt
      8. Assert: First row shows selection indicator
      9. tmux send-keys -t schedule-select "j"  # Move down
      10. tmux send-keys -t schedule-select "Tab"  # Select second
      11. sleep 0.3
      12. tmux capture-pane -t schedule-select -p > /tmp/select-2.txt
      13. Assert: Both rows show selection indicator
      14. tmux send-keys -t schedule-select "q"
      15. task +selecttest delete rc.confirmation:off
      16. tmux kill-session -t schedule-select 2>/dev/null || true
    Expected Result: Multiple tasks can be selected
    Evidence: Screenshots captured

  Scenario: Shift+A selects all visible tasks
    Tool: interactive_bash (tmux)
    Preconditions: Package installed, multiple tasks exist
    Steps:
      1. task add "SelectAll Test 1" +selectalltest
      2. task add "SelectAll Test 2" +selectalltest
      3. task add "SelectAll Test 3" +selectalltest
      4. tmux new-session -d -s schedule-selectall "uv run schedule"
      5. sleep 2
      6. tmux send-keys -t schedule-selectall "A"  # Shift+A = capital A
      7. sleep 0.5
      8. tmux capture-pane -t schedule-selectall -p > /tmp/selectall.txt
      9. cat /tmp/selectall.txt
      10. Assert: All visible rows show selection indicator
      11. tmux send-keys -t schedule-selectall "q"
      12. task +selectalltest delete rc.confirmation:off
      13. tmux kill-session -t schedule-selectall 2>/dev/null || true
    Expected Result: All tasks selected at once
    Evidence: Screenshot captured

  Scenario: Selection clears after batch operation
    Tool: interactive_bash (tmux)
    Preconditions: Package installed
    Steps:
      1. task add "BatchClear Test 1" +batchcleartest
      2. task add "BatchClear Test 2" +batchcleartest
      3. tmux new-session -d -s schedule-batchclear "uv run schedule"
      4. sleep 2
      5. tmux send-keys -t schedule-batchclear "Tab"  # Select first
      6. tmux send-keys -t schedule-batchclear "j"
      7. tmux send-keys -t schedule-batchclear "Tab"  # Select second
      8. sleep 0.3
      9. tmux send-keys -t schedule-batchclear "1"  # Schedule both
      10. sleep 1
      11. tmux capture-pane -t schedule-batchclear -p > /tmp/batchclear.txt
      12. Assert: No selection indicators visible (cleared)
      13. tmux send-keys -t schedule-batchclear "q"
      14. task +batchcleartest delete rc.confirmation:off
      15. tmux kill-session -t schedule-batchclear 2>/dev/null || true
    Expected Result: Selection cleared after operation
    Evidence: Screenshot captured
  ```

  **Commit**: YES
  - Message: `feat(ui): multi-select with Tab and Shift+A`
  - Files: `src/schedule/app.py`, `src/schedule/widgets/task_table.py`
  - Pre-commit: None

---

- [x] 6. Hotkey System (with Batch Support)

  **What to do**:
  - Implement key bindings in App:
    ```python
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("w", "toggle_wait", "Wait"),
        ("s", "toggle_scheduled", "Scheduled"),
        ("d", "toggle_due", "Due"),
        ("r", "change_report", "Report"),
        ("0", "clear_date", "Clear"),
        ("1", "schedule_1", "1"),
        ("2", "schedule_2", "2"),
        # ... etc for 3-9
        ("tab", "toggle_selection", "Select"),
        ("A", "select_all", "All"),
    ]
    ```
  - Implement action methods:
    - `action_toggle_*`: Toggle date field, update header chips
    - `action_schedule_N`: 
      - Get hotkey value from config
      - Get selected tasks (or current if none selected)
      - **For each selected task**: call TW modify for active date fields
      - **Clear selection after batch operation**
    - `action_clear_date`: Same batch logic as schedule
  - After any modify: refresh task list
  - Show toast on error (individual task errors don't stop batch)

  **Must NOT do**:
  - Don't add confirmation dialogs (unless config says so)
  - Don't add undo

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Straightforward key binding implementation
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 7)
  - **Blocks**: Task 8
  - **Blocked By**: Tasks 4, 5, 5b (needs toggle manager, UI, and multi-select)

  **References**:
  - **External**: Textual Bindings: https://textual.textualize.io/guide/input/#bindings
  - **Pattern**: Dooit keybindings: https://github.com/dooit-org/dooit/blob/main/dooit/utils/default_config.py

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: Hotkey 1 schedules task to tomorrow
    Tool: interactive_bash (tmux)
    Preconditions: Package installed
    Steps:
      1. task add "Hotkey Test Task" +hotkeytest
      2. UUID=$(task +hotkeytest export | uv run python -c "import sys,json; print(json.load(sys.stdin)[0]['uuid'])")
      3. tmux new-session -d -s schedule-hotkey "uv run schedule"
      4. sleep 2
      5. tmux send-keys -t schedule-hotkey "1"  # Press hotkey 1
      6. sleep 1
      7. tmux send-keys -t schedule-hotkey "q"
      8. sleep 1
      9. task uuid:$UUID export | grep -q "scheduled"
      10. Assert: Exit code 0 (scheduled field was set)
      11. task +hotkeytest delete rc.confirmation:off
      12. tmux kill-session -t schedule-hotkey 2>/dev/null || true
    Expected Result: Task has scheduled date set
    Evidence: Task export shows scheduled field

  Scenario: Toggle W/S/D updates header
    Tool: interactive_bash (tmux)
    Preconditions: Package installed
    Steps:
      1. tmux new-session -d -s schedule-toggle "uv run schedule"
      2. sleep 2
      3. tmux send-keys -t schedule-toggle "d"  # Toggle due
      4. sleep 0.5
      5. tmux capture-pane -t schedule-toggle -p > /tmp/toggle-output.txt
      6. cat /tmp/toggle-output.txt
      7. Assert: Header shows both S and D as active (chips)
      8. tmux send-keys -t schedule-toggle "q"
      9. tmux kill-session -t schedule-toggle 2>/dev/null || true
    Expected Result: Header reflects active fields
    Evidence: Screenshot captured

  Scenario: Hotkey 0 clears date field
    Tool: interactive_bash (tmux)
    Preconditions: Package installed, task with scheduled date exists
    Steps:
      1. task add "Clear Test Task" scheduled:tomorrow +cleartest
      2. UUID=$(task +cleartest export | uv run python -c "import sys,json; print(json.load(sys.stdin)[0]['uuid'])")
      3. tmux new-session -d -s schedule-clear "uv run schedule"
      4. sleep 2
      5. tmux send-keys -t schedule-clear "0"  # Clear
      6. sleep 1
      7. tmux send-keys -t schedule-clear "q"
      8. sleep 1
      9. SCHED=$(task uuid:$UUID export | uv run python -c "import sys,json; t=json.load(sys.stdin)[0]; print(t.get('scheduled', 'NONE'))")
      10. Assert: SCHED is "NONE" or empty
      11. task +cleartest delete rc.confirmation:off
      12. tmux kill-session -t schedule-clear 2>/dev/null || true
    Expected Result: Scheduled field is cleared
    Evidence: Task export shows no scheduled field

  Scenario: Batch scheduling modifies multiple selected tasks
    Tool: interactive_bash (tmux)
    Preconditions: Package installed
    Steps:
      1. task add "Batch Test 1" +batchtest
      2. task add "Batch Test 2" +batchtest
      3. UUID1=$(task +batchtest export | uv run python -c "import sys,json; tasks=json.load(sys.stdin); print(tasks[0]['uuid'])")
      4. UUID2=$(task +batchtest export | uv run python -c "import sys,json; tasks=json.load(sys.stdin); print(tasks[1]['uuid'])")
      5. tmux new-session -d -s schedule-batch "uv run schedule"
      6. sleep 2
      7. tmux send-keys -t schedule-batch "Tab"  # Select first
      8. sleep 0.2
      9. tmux send-keys -t schedule-batch "j"    # Move to second
      10. tmux send-keys -t schedule-batch "Tab"  # Select second
      11. sleep 0.2
      12. tmux send-keys -t schedule-batch "1"    # Schedule both to tomorrow
      13. sleep 1
      14. tmux send-keys -t schedule-batch "q"
      15. sleep 1
      16. task uuid:$UUID1 export | grep -q "scheduled"
      17. Assert: Exit code 0 (first task has scheduled)
      18. task uuid:$UUID2 export | grep -q "scheduled"
      19. Assert: Exit code 0 (second task has scheduled)
      20. task +batchtest delete rc.confirmation:off
      21. tmux kill-session -t schedule-batch 2>/dev/null || true
    Expected Result: Both selected tasks were scheduled
    Evidence: Task exports show scheduled fields
  ```

  **Commit**: YES
  - Message: `feat(hotkeys): scheduling hotkeys 0-9 and W/S/D toggles`
  - Files: `src/schedule/app.py`
  - Pre-commit: None (manual TUI testing)

---

- [x] 7. Report Change Modal

  **What to do**:
  - Create `ReportModal` as `ModalScreen` subclass
  - Contains single `Input` widget for report name
  - On submit: update app's current report, reload tasks
  - On cancel (Escape): close without changes
  - Wire up to "R" key in main app

  **Must NOT do**:
  - Don't add report suggestions/autocomplete
  - Don't validate report name (TW will error if invalid)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple modal with input field
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 6)
  - **Blocks**: Task 8
  - **Blocked By**: Task 5 (needs UI core)

  **References**:
  - **External**: Textual ModalScreen: https://textual.textualize.io/guide/screens/#modal-screens
  - **External**: Textual Input: https://textual.textualize.io/widgets/input/

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: R opens report modal
    Tool: interactive_bash (tmux)
    Preconditions: Package installed
    Steps:
      1. tmux new-session -d -s schedule-modal "uv run schedule"
      2. sleep 2
      3. tmux send-keys -t schedule-modal "r"  # Open modal
      4. sleep 0.5
      5. tmux capture-pane -t schedule-modal -p > /tmp/modal-output.txt
      6. cat /tmp/modal-output.txt
      7. Assert: Shows input field or modal overlay
      8. tmux send-keys -t schedule-modal "Escape"  # Cancel
      9. sleep 0.5
      10. tmux send-keys -t schedule-modal "q"
      11. tmux kill-session -t schedule-modal 2>/dev/null || true
    Expected Result: Modal appears and can be cancelled
    Evidence: Screenshot captured

  Scenario: Entering report name reloads tasks
    Tool: interactive_bash (tmux)
    Preconditions: Package installed, "all" report exists in TW
    Steps:
      1. tmux new-session -d -s schedule-report "uv run schedule"
      2. sleep 2
      3. tmux send-keys -t schedule-report "r"
      4. sleep 0.5
      5. tmux send-keys -t schedule-report "all"
      6. tmux send-keys -t schedule-report "Enter"
      7. sleep 1
      8. tmux capture-pane -t schedule-report -p
      9. Assert: Header shows "all" as current report
      10. tmux send-keys -t schedule-report "q"
      11. tmux kill-session -t schedule-report 2>/dev/null || true
    Expected Result: Report changed and displayed
    Evidence: Screenshot shows "all" report
  ```

  **Commit**: YES
  - Message: `feat(ui): report change modal`
  - Files: `src/schedule/widgets/report_modal.py`
  - Pre-commit: None

---

- [x] 8. Integration, Polish & Final Verification

  **What to do**:
  - Ensure all components work together
  - Verify footer shows all shortcuts correctly:
    - W/S/D toggles with current state
    - R for report
    - 0 for clear
    - 1-9 with their configured values (only show configured ones)
    - q for quit
  - Test error scenarios (TW not available, invalid report)
  - Verify toast notifications appear on errors
  - Add `main()` function in `main.py` that instantiates app and runs it
  - Ensure `uv tool install .` works end-to-end

  **Must NOT do**:
  - Don't add new features
  - Don't refactor working code
  - Don't add documentation beyond code comments

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Integration testing, minor fixes
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (final task)
  - **Blocks**: None (final)
  - **Blocked By**: Tasks 6, 7

  **References**:
  - All previous task outputs

  **Acceptance Criteria**:

  **Agent-Executed QA Scenarios:**

  ```
  Scenario: End-to-end workflow
    Tool: interactive_bash (tmux)
    Preconditions: Package installed, TaskWarrior configured
    Steps:
      1. task add "E2E Test Task" project:E2ETest +e2etest
      2. uv tool install . --force
      3. tmux new-session -d -s schedule-e2e "schedule"  # Run installed tool
      4. sleep 2
      5. tmux capture-pane -t schedule-e2e -p > /tmp/e2e-initial.txt
      6. Assert: Task list visible with "E2E Test Task"
      7. tmux send-keys -t schedule-e2e "d"  # Toggle due
      8. sleep 0.3
      9. tmux send-keys -t schedule-e2e "1"  # Schedule to tomorrow
      10. sleep 1
      11. tmux capture-pane -t schedule-e2e -p > /tmp/e2e-after.txt
      12. tmux send-keys -t schedule-e2e "q"
      13. sleep 1
      14. task +e2etest export > /tmp/e2e-task.json
      15. Assert: JSON contains "scheduled" field
      16. Assert: JSON contains "due" field (both were set)
      17. task +e2etest delete rc.confirmation:off
      18. tmux kill-session -t schedule-e2e 2>/dev/null || true
    Expected Result: Full workflow completes
    Evidence: Screenshots and task export saved

  Scenario: Footer shows configured hotkeys
    Tool: interactive_bash (tmux)
    Preconditions: Package installed
    Steps:
      1. echo "hotkeys:
           1: tomorrow
           2: '+2d'
           3: '+3d'" > /tmp/hotkey-config.yaml
      2. SCHEDULE_CONFIG_FILE=/tmp/hotkey-config.yaml tmux new-session -d -s schedule-footer "uv run schedule"
      3. sleep 2
      4. tmux capture-pane -t schedule-footer -p > /tmp/footer-output.txt
      5. cat /tmp/footer-output.txt
      6. Assert: Footer contains "1" and "tomorrow" (or abbreviated)
      7. Assert: Footer contains "2" and "+2d" (or abbreviated)
      8. Assert: Footer does NOT show 6-9 (not configured)
      9. tmux send-keys -t schedule-footer "q"
      10. tmux kill-session -t schedule-footer 2>/dev/null || true
    Expected Result: Footer reflects config
    Evidence: Screenshot captured

  Scenario: Error toast on invalid TW command
    Tool: interactive_bash (tmux)
    Preconditions: Package installed
    Steps:
      1. echo "default_report: nonexistent_report_xyz" > /tmp/bad-report.yaml
      2. SCHEDULE_CONFIG_FILE=/tmp/bad-report.yaml tmux new-session -d -s schedule-error "uv run schedule"
      3. sleep 2
      4. tmux capture-pane -t schedule-error -p
      5. Assert: Shows error notification or empty state (not crash)
      6. tmux send-keys -t schedule-error "q"
      7. tmux kill-session -t schedule-error 2>/dev/null || true
    Expected Result: Graceful error handling
    Evidence: Screenshot captured
  ```

  **Commit**: YES
  - Message: `feat(schedule): complete integration and polish`
  - Files: `src/schedule/main.py`, any fixes
  - Pre-commit: `uv tool install . && schedule --help || schedule &; sleep 2; kill %1`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `feat(init): project structure and pyproject.toml` | pyproject.toml, src/schedule/** | `uv pip install -e .` |
| 2 | `feat(config): YAML config loading with XDG support` | config.py | Python import |
| 3 | `feat(taskwarrior): subprocess wrapper for TW CLI` | taskwarrior.py | Python import |
| 4+5 | `feat(ui): core app layout with DataTable and navigation` | app.py, widgets/, app.tcss | App starts |
| 6 | `feat(hotkeys): scheduling hotkeys 0-9 and W/S/D toggles` | app.py | Manual test |
| 7 | `feat(ui): report change modal` | report_modal.py | Manual test |
| 8 | `feat(schedule): complete integration and polish` | main.py | `uv tool install .` |

---

## Success Criteria

### Verification Commands
```bash
# Install and run
uv tool install .
schedule  # Should start TUI

# Verify config loading
SCHEDULE_CONFIG_FILE=/tmp/test.yaml schedule

# Verify TW integration (in app)
# - Press 1 on a task → task gets scheduled:tomorrow
# - Press W to toggle wait field
# - Press R, enter "all", press Enter → report changes
```

### Final Checklist
- [x] All "Must Have" features present and working
- [x] All "Must NOT Have" exclusions respected (no extras)
- [x] App installable via `uv tool install .`
- [x] Config loads from XDG path and ENV override
- [x] Hotkeys 1-9 + 0 modify correct date fields
- [x] W/S/D toggles work additively
- [x] R opens report modal
- [x] j/k and arrow navigation works
- [x] q quits the app
- [x] Errors show as toast notifications
- [x] **Tab toggles task selection**
- [x] **Shift+A selects all visible tasks**
- [x] **Hotkeys work on all selected tasks (batch)**
- [x] **Selection clears after batch operation**
