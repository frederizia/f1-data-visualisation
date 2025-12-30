.PHONY: install_dependencies
install_dependencies:
	uv sync --group dev --inexact
	@if [ -f requirements/local.txt ]; then \
		uv pip install -r requirements/local.txt; \
	fi


.PHONY: precommit
precommit:
	pre-commit install


.PHONY: format
format:
	uv run ruff format .
	uv run ruff check --fix .


.PHONY: ty
ty:
	uv run ty check


.PHONY: test
test:
	uv run pytest tests
