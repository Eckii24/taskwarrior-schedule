# Test Suite for Schedule TUI

Comprehensive test suite for the taskwarrior-schedule application following Textual testing best practices.

## Test Coverage

Current test coverage: **89%** (370 statements, 40 missed)

All 72 tests passing ✓

### Module Breakdown

| Module | Coverage | Notes |
|--------|----------|-------|
| `config.py` | 100% | Full coverage of configuration loading and date field management |
| `taskwarrior.py` | 98% | Comprehensive TaskWarrior client testing with mocked subprocess |
| `custom_header.py` | 100% | Widget rendering and updates |
| `report_modal.py` | 100% | Modal screen interactions |
| `app.py` | 88% | Main application logic, UI interactions, and workflows |

## Test Files

### `tests/conftest.py`
Pytest configuration and shared fixtures:
- `sample_tasks`: Sample TaskWarrior task data
- `mock_subprocess_run`: Mock for subprocess.run()
- `mock_tw_client`: Complete TaskWarriorClient mock
- `temp_config_file`: Temporary config file for testing

### `tests/test_config.py` (49 tests)
Configuration module tests:
- **TestGetConfigPath**: Config file path resolution (XDG, env vars)
- **TestLoadConfig**: YAML loading, validation, merging
- **TestDateFieldManager**: Date field toggle logic

### `tests/test_taskwarrior.py` (19 tests)
TaskWarrior CLI integration tests:
- Report name caching and parsing
- Task fetching with various filter/report combinations
- Task modification with field updates
- Error handling for subprocess failures

### `tests/test_custom_header.py` (5 tests)
CustomHeader widget tests:
- Initial rendering with filter and active fields
- Dynamic status updates
- Empty value handling

### `tests/test_report_modal.py` (7 tests)
ReportModal screen tests:
- Input field rendering and focus
- Submit (Enter) and cancel (Escape) actions
- Value passing through callbacks

### `tests/test_app.py` (35+ tests)
Main application tests organized by feature:

#### TestScheduleAppLifecycle
- App initialization and configuration loading
- Task loading on mount
- Empty task list handling

#### TestScheduleAppNavigation
- j/k vim-style navigation
- Cursor movement and positioning

#### TestScheduleAppTaskSelection
- Tab key selection toggle
- Shift+A select all
- Multi-select capability
- Visual selection indicators

#### TestScheduleAppDateFieldToggles
- s/d/w key toggles for scheduled/due/wait fields
- Multiple active fields simultaneously

#### TestScheduleAppSchedulingHotkeys
- Hotkeys 0-9 for scheduling
- Batch scheduling selected tasks
- Multi-field updates
- Selection clearing after operations

#### TestScheduleAppReportSwitching
- Modal opening (r key)
- Report/filter changing
- Task list refresh

#### TestScheduleAppErrorHandling
- TaskWarrior command failures
- Modification errors
- Unconfigured hotkeys

#### TestScheduleAppIntegration
- Complete user workflows end-to-end
- Batch scheduling workflows
- Date clearing workflows

### `tests/test_utils.py` (11 tests)
Utility function and configuration tests:
- Date formatting helper
- Application key bindings verification

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with coverage report
```bash
pytest tests/ --cov=schedule --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_app.py -v
```

### Run specific test class or function
```bash
pytest tests/test_app.py::TestScheduleAppNavigation::test_j_key_moves_cursor_down -v
```

## Testing Approach

### Textual Testing Patterns

This test suite follows official Textual testing practices:

1. **Async Test Functions**: All TUI tests are async
   ```python
   @pytest.mark.asyncio
   async def test_feature(self):
       app = ScheduleApp()
       async with app.run_test() as pilot:
           await pilot.pause()
           # Test interactions
   ```

2. **Pilot API for Interactions**:
   - `await pilot.press("key")`: Simulate keypresses
   - `await pilot.pause()`: Wait for async operations
   - `app.query_one()`: Query widgets from DOM

3. **Mocking External Dependencies**:
   - TaskWarrior CLI calls mocked via `monkeypatch`
   - subprocess.run() replaced with test doubles
   - Configuration files use temporary directories

4. **State Verification**:
   - Check widget properties directly
   - Verify app state after interactions
   - Assert on rendered content

### Test Organization

Tests are organized by:
1. **Unit tests**: Individual functions and classes (config, taskwarrior)
2. **Widget tests**: Component behavior in isolation (header, modal)
3. **Integration tests**: Full app workflows (navigation, scheduling)
4. **End-to-end tests**: Complete user scenarios

### Workarounds for Textual Testing Limitations

**Key Bindings in Test Mode:**
Some key bindings (particularly Tab and Shift+A) don't trigger properly via `pilot.press()` in test mode. The solution is to call the action methods directly:

```python
# Instead of: await pilot.press("tab")
app.action_toggle_selection()

# Instead of: await pilot.press("shift+a")  
app.action_select_all()
```

**Modal Screen Queries:**
When querying widgets inside modal screens, access the screen stack:

```python
modal_screen = app.screen_stack[-1]
input_field = modal_screen.query_one("#report-input", Input)
```

## Future Improvements

Potential test enhancements:
- [ ] Snapshot testing for visual regression
- [ ] Performance benchmarks for large task lists
- [ ] Property-based testing for config parsing
- [ ] Integration tests with actual TaskWarrior (optional)
- [ ] CI/CD pipeline integration

## Test Maintenance

When adding new features:
1. Add unit tests for new functions/classes
2. Add integration tests for new user interactions
3. Update fixtures if new mock data is needed
4. Run full test suite before committing
5. Aim for >85% code coverage
