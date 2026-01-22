# Agent Guidelines for onthefly

This document provides essential information for AI coding agents working on the `onthefly` codebase.

## Project Overview

**onthefly** is a Python CLI tool that emulates typing by allowing you to "type" file contents by pressing keyboard keys (asdfjkl;). It's designed for live coding presentations and works with any text editor on Linux.

- **Language**: Python 3.5+
- **Framework**: Click (CLI framework)
- **Platform**: Linux only (uses evdev)
- **Package Type**: Standard Python package with setuptools

## Build, Lint, and Test Commands

### Quick Reference

```bash
# Linting
make lint                    # Check code style with flake8
flake8 onthefly tests       # Direct flake8 invocation

# Testing
make test                    # Run tests quickly with default Python
pytest                       # Run tests with pytest (recommended)
make test-all               # Run tests across all Python versions with tox
make coverage               # Run tests with coverage report

# Running specific tests
python -m unittest tests.test_onthefly                           # Run test module
pytest tests/test_onthefly.py                                    # Run test file
pytest tests/test_onthefly.py::TestOnthefly::test_method_name   # Run specific test

# Building
make dist                    # Build source and wheel package
make install                # Install package locally

# Cleaning
make clean                  # Remove all build/test artifacts
make clean-pyc             # Remove Python file artifacts only
make clean-test            # Remove test and coverage artifacts only

# Documentation
make docs                   # Generate Sphinx HTML documentation
cd docs && make html        # Alternative documentation build
```

### Development Setup

```bash
git clone <repo-url>
cd onthefly/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_dev.txt
python setup.py develop
```

## Code Style Guidelines

### Linting Configuration

- **Linter**: flake8 3.7.8
- **Config**: `setup.cfg` → `[flake8]` section
- **Excluded**: `docs/` directory
- **Enforcement**: Run `make lint` before committing
- **Standard**: PEP 8 compliance

### Formatting

- **Indentation**: 4 spaces (defined in `.editorconfig`)
- **Line endings**: LF (Unix-style)
- **Encoding**: UTF-8
- **Trailing whitespace**: Remove
- **Final newline**: Always insert
- **No automatic formatter**: Black, autopep8, or yapf are NOT configured

### Import Organization

Organize imports in three groups with blank lines between:

```python
# 1. Standard library imports
import sys
import time
from pathlib import Path

# 2. Third-party imports
import click
from evdev import UInput, ecodes, InputDevice
from configparser import ConfigParser

# 3. Local/application imports
from onthefly.onthefly import onthefly
```

### Naming Conventions

- **Functions**: `snake_case` (e.g., `read_input_file`, `simulate_key_press`)
- **Variables**: `snake_case` (e.g., `keyboard_device_path`, `char_idx`)
- **Constants**: `UPPER_CASE` (e.g., `WRITE_NEXT_CHAR_KEYS`)
- **Modules**: `snake_case` (e.g., `onthefly.py`)
- **Classes**: Not applicable (minimal OOP in this codebase)

### Type Hints

**NOT USED** in this codebase. Do not add type hints unless explicitly requested, as the project maintains compatibility with Python 3.5+ where type hints were less common.

### Function Style

- Keep functions small and focused (3-10 lines typical)
- Use descriptive names that indicate purpose
- Early returns for error conditions
- Clear separation of concerns

Example:
```python
def simulate_key(ui, code, keystate):
    ui.write(ecodes.EV_KEY, code, keystate)
    ui.syn()
```

### Docstrings and Comments

- **Module docstrings**: Use triple double quotes at file top
- **Function docstrings**: Minimal; most functions lack detailed docstrings
- **Inline comments**: Use frequently for clarity
- **Style**: Simple, descriptive strings

Example:
```python
# give time for packages to initialize properly
time.sleep(0.1)
```

### Error Handling

- Minimal use of try/except blocks
- Bare except used sparingly (e.g., config reading fallback)
- Prefer early exits with clear error messages
- Print helpful error messages to stdout

Example:
```python
if keyboard_device_path not in list_devices():
    print("Error: No keyboard found.\n\nUse...")
    sys.exit()
```

### Code Organization

- Define helper functions before they are used
- Group related functions together
- Main logic in primary function (e.g., `onthefly()`)
- Configuration/constants at module top

## Testing Standards

### Test Framework

- **Primary**: pytest 7.2.0
- **Secondary**: unittest (standard library)
- **Location**: `/tests/test_onthefly.py`

### Test Requirements

- Include tests with new functionality
- Run `make test` before submitting PRs
- Use `make coverage` to check test coverage
- Run `tox` for multi-version compatibility (Python 3.5-3.10)

### CI/CD

- **Platform**: Travis CI
- **Tested versions**: Python 3.5, 3.6, 3.7, 3.8, 3.9, 3.10
- **Auto-deploy**: On tag push to PyPI

## Version Management

- **Tool**: bump2version
- **Current**: 1.1.7
- **Command**: `bump2version [patch|minor|major]`
- **Workflow**: Bump → commit → tag → push → push tags → CI deploys

## Project Structure

```
onthefly/
├── onthefly/              # Main package
│   ├── __init__.py       # Package metadata (__version__)
│   ├── cli.py            # CLI entry point (Click)
│   └── onthefly.py       # Core functionality (220 lines)
├── tests/                # Test suite
│   └── test_onthefly.py  # Unit tests
├── docs/                 # Sphinx documentation
├── examples/             # Example input files
├── setup.py              # Package configuration
├── setup.cfg             # Tool configurations
├── Makefile              # Build automation
├── tox.ini               # Multi-environment testing
└── requirements_dev.txt  # Development dependencies
```

## Dependencies

### Runtime
- `Click>=7.0` - CLI framework
- `evdev` - Linux input device interface
- `appdirs` - Platform-specific directories
- `elevate` - Privilege escalation

### Development
- `pytest==7.2.0` - Testing
- `flake8==3.7.8` - Linting
- `coverage==4.5.4` - Code coverage
- `tox==3.14.0` - Multi-version testing

## Pre-commit Checklist

Before committing changes:

1. ✓ Run `make lint` - ensure flake8 passes
2. ✓ Run `make test` - ensure all tests pass
3. ✓ Add tests for new functionality
4. ✓ Update documentation if needed
5. ✓ Follow existing code style (snake_case, 4 spaces)
6. ✓ Check imports are organized correctly
7. ✓ Remove trailing whitespace
8. ✓ Ensure final newline in all files

## Commit Message Style

Based on git history:

- Use imperative mood: "Add feature" not "Added feature"
- Be concise and descriptive
- Examples:
  - "Bump version to 1.1.7"
  - "Remove delays that fixed not correctly capturing LEFTSHIFT key presses"
  - "Update twine and urllib3"

## Security Considerations

- **Requires root**: Tool uses `elevate` package for privilege escalation
- **Device access**: Directly interfaces with `/dev/input/event*` devices
- **Input grabbing**: Uses `dev.grab()` to intercept keyboard events

## Platform Limitations

- **Linux only**: Uses evdev, which is Linux-specific
- **Keyboard device**: Requires identifying keyboard device path
- **Discovery**: Use `sudo python -m evdev.evtest` to find device

## Common Tasks

### Adding a new key mapping
1. Update `ascii2keycode` or `shift_ascii2keycode` dict in `onthefly/onthefly.py`
2. Add test case in `tests/test_onthefly.py`
3. Run tests and linting

### Adding a new CLI option
1. Edit `onthefly/cli.py` using Click decorators
2. Update `onthefly/onthefly.py` function signature
3. Update documentation in `docs/usage.rst`

### Release process
1. Update HISTORY.rst with changes
2. Run `bump2version [patch|minor|major]`
3. Run `git push && git push --tags`
4. Travis CI will build and deploy to PyPI

## References

- Main docs: `/docs/`
- Contributing: `CONTRIBUTING.rst`
- README: `README.rst`
- License: MIT
- PyPI: https://pypi.python.org/pypi/onthefly
