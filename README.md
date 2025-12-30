# F1 data visualisation

This is a project to play around with some F1 data and visualise it. This is not
intended to be deployed anywhere, it's just for local exploration and learning.

The plan is to
* use `fastf1` to get F1 data
* store the data in the database using `sqlalchemy`
* use `streamlit` to display the data

The focus is a driver season and career view, as opposed to telemetry data.

## Basic setup

This project requires Python 3.13.3, as specified in `.python_version`.

It also requires `uv` to be installed, which can be done using e.g.
```shell
  pip install uv
```

As we're using uv, this means all commands can be run with `uv run <your-command>` which
will use the virtual environment created by `uv` in the `.venv` directory.

## Adding dependencies

New dependencies can be added by running

```shell
  uv add <package-name>
```

and installed using

```shell
  uv sync
```
though any `uv run <command>` will also install missing dependencies. Commit any changes to the `pyproject.toml` and
`uv.lock` files.

Local (developer only) dependencies can be added to `requirements/local.txt` and
installed using

```shell
  make install_dependencies
```

## Local development

When starting to work on this project, you can simply run

```shell
    make dev
```
to copy the default `.env` file, install dependencies and the pre-commit hooks.

Otherwise, pre-commit can be set up using:

```shell
  make precommit
```
`
This project uses ruff for linting and formatting. You can run these manually using

```shell
  make format
```

Type checking can be run using

```shell
  make ty
```

Tests can be run using

```shell
  make test
```

## Database

This project uses a PostgresQL 16 database. You can create (or recreate) a local database using
```shell
  make reset_database
```

Other useful commands for database management are:

```shell
  make run_db_migrations      # Run pending database migrations
  make downgrade_db_migration # Downgrade to previous migration
  make build_migration        # Create a new migration (requires MESSAGE env var)
```

For example, to create a new migration:
```shell
  make build_migration MESSAGE="Add users table"
```



-----

This project was created using the [simply Python project cookiecutter](https://github.com/frederizia/simple-python-project-cookiecutter).
