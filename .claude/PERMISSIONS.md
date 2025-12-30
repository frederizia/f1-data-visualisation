# Claude Code Permissions

This document explains the permissions configured in `settings.json` for Claude Code in this project.

## Overview

The `.claude/settings.json` file defines which commands Claude Code is allowed to run in your project. Permissions are organized into three categories:

- **allow**: Commands that Claude Code can run without asking
- **deny**: Commands that Claude Code cannot run
- **ask**: Commands that Claude Code will ask for permission before running

To add personal settings, create a `.claude/settings.local.json` file that overrides or extends these permissions.

## Allowed Permissions

### Web Access
- **`WebFetch(domain:*)`** - Allows fetching content from any website

### Type Checking
- **`Bash(ty:*)`** - Runs `ty` command (a tool for type checking)
- **`Bash(uv run ty:*)`** - Runs type checking via uv package manager
- **`Bash(.venv/bin/ty:*)`** - Runs type checking from virtual environment

### Python Execution
- **`Bash(.venv/bin/python:*)`** - Runs Python from the virtual environment

### Build Tools
- **`Bash(make:*)`** - Runs make commands

### Utilities
- **`Bash(cat:*)`** - Reads file contents

### Testing
- **`Bash(uv run pytest:*)`** - Runs pytest via uv package manager
- **`Bash(pytest:*)`** - Runs pytest directly
- **`Bash(python -m pytest:*)`** - Runs pytest as a Python module
- **`Bash(.venv/bin/pytest:*)`** - Runs pytest from virtual environment
- **`Bash(.venv/bin/python -m pytest:*)`** - Runs pytest from virtual environment as a module

### Code Quality
- **`Bash(uv run ruff:*)`** - Runs ruff linter via uv package manager

### Git Commands (Read-Only)
- **`Bash(git status:*)`** - View repository status
- **`Bash(git log:*)`** - View commit history
- **`Bash(git show:*)`** - Show commit details
- **`Bash(git diff:*)`** - View differences between commits or working tree
- **`Bash(git branch:*)`** - View and manage branches
- **`Bash(git remote:*)`** - Manage remote repositories
- **`Bash(git ls-files:*)`** - List tracked files
- **`Bash(git ls-tree:*)`** - List tree structure
- **`Bash(git rev-parse:*)`** - Parse Git references
- **`Bash(git describe:*)`** - Describe commits
- **`Bash(git blame:*)`** - Show commit attribution
- **`Bash(git reflog:*)`** - View reference logs
- **`Bash(git config --get:*)`** - Read Git configuration
- **`Bash(git fetch:*)`** - Fetch from remote repositories
