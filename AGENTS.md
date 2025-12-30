# AI Agent Coding Guidelines

This document provides guidance for AI coding agents (including Claude Code at claude.ai/code) when working with code in this repository.

## Project Overview

This is a simple Python project template using modern development tools and best practices.

**Tech Stack:**
- Python 3.13+
- `uv` for dependency management
- `ruff` for linting and formatting
- `pytest` for testing
- `ty` for type checking

## Common Commands

### Development Setup
```bash
make precommit              # Install pre-commit hooks
uv sync                     # Install dependencies
```

### Running Tests
```bash
make test                   # Run all tests
uv run pytest               # Run tests with pytest directly
uv run pytest tests/        # Run tests from tests directory
uv run pytest path/to/test_file.py  # Run specific test file
```

### Code Quality

```bash
make format                 # Auto-format code with ruff
make ty                     # Run type checking with ty
uv run ruff check .         # Run ruff linter
```

### Package Management
```bash
uv add <package>            # Add production dependency
uv add --dev <package>      # Add dev dependency
uv remove <package>         # Remove dependency
uv sync --upgrade           # Upgrade all packages
```

## Project Structure

```
src/f1_data_visualisation/
├── __init__.py             # Package initialization
└── main.py                 # Main application code

tests/
├── f1_data_visualisation/
│   └── unit/
│       ├── __init__.py
│       └── test_main.py    # Unit tests
```

## Coding Standards

### Type Hints

- Type hints are required in production code
- Tests do not require type hints (see `pyproject.toml` ruff configuration)
- Use clear, descriptive types

### Code Style

**Ruff Configuration:**
- Line length: 99 characters
- Selects all rules (`select = ["ALL"]`)
- Tests and `__init__.py` files have relaxed rules
- See `pyproject.toml` for detailed rule configuration

### Test Code Style

- Use descriptive test names that explain what is being tested
- Keep tests focused and isolated
- Prefer simple, readable assertions
- Comments can be used to clarify test intent
- Test functions should be grouped in classes that mirror the function name, e.g. `TestFunctionName`
- Don't use docstrings in test functions, the name should be descriptive enough, e.g. `def test_function_does_x_when_y():`

## Pre-Commit Hooks

Pre-commit hooks are configured to run automatically before commits. These ensure:
- Code is formatted with ruff
- Linting rules pass
- Type checking passes
- Tests pass (depending on configuration)

Run `make precommit` to install hooks locally.

## Additional Resources

- See `README.md` for setup and basic usage instructions
