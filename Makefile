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


.PHONY: test_from_fresh_db
test_from_fresh_db:
    # We want to be able to run tests on a brand new database and we don't want to compromise our local one.
	dropdb f1data-test --if-exists
	createdb f1data-test
	DATABASE_URL="postgresql://postgres@localhost/f1data-test" make run_db_migrations
	DATABASE_URL="postgresql://postgres@localhost/f1data-test" uv run pytest tests


.PHONY:import_linter
import_linter:
	uv run lint-imports


.env:
	cp .env.default .env


.PHONY: dev
dev: .env install_dependencies precommit


.PHONY: run_python
run_python:
	uv run python


.PHONY: run_api
run_api:
	uv run uvicorn src.f1_data_visualisation.interfaces.api.main:app --reload


# Database related commands
.PHONY: run_db_migrations
run_db_migrations:
	uv run alembic -c ./src/f1_data_visualisation/data/alembic.ini upgrade head


.PHONY: downgrade_db_migration
downgrade_db_migration:
	uv run alembic -c ./src/f1_data_visualisation/data/alembic.ini downgrade -1


.PHONY: build_migration
build_migration:
	uv run alembic -c ./src/f1_data_visualisation/data/alembic.ini revision --autogenerate -m "$(MESSAGE)"


.PHONY: reset_database
reset_database:
	dropdb f1data --if-exists
	createdb f1data
	make run_db_migrations


.PHONY: discover_missing_migrations
discover_missing_migrations:
    # Create a temporary database to test migrations.
	dropdb f1data-migrations --if-exists
	createdb f1data-migrations
	DATABASE_URL="postgresql://postgres@localhost/f1data-migrations" make run_db_migrations
	DATABASE_URL="postgresql://postgres@localhost/f1data-migrations" uv run alembic -c src/f1_data_visualisation/data/alembic.ini check
