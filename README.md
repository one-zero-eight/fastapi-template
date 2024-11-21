# FastAPI Template

## About

This is the CookieCutter template for FastAPI ASGI application.

### Technologies

- [Python 3.12](https://www.python.org/downloads/) & [Poetry](https://python-poetry.org/docs/)
- [FastAPI](https://fastapi.tiangolo.com/)
- Database and ORM:
    - [PostgreSQL](https://www.postgresql.org/), [SQLAlchemy](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/en/latest/)
    - OR [MongoDB](https://www.mongodb.com/) & [Beanie](https://beanie-odm.dev/)
- Formatting and linting: [Ruff](https://docs.astral.sh/ruff/), [pre-commit](https://pre-commit.com/)
- Deployment: [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/),
  [GitHub Actions](https://github.com/features/actions)

## How to use?

1. Install [Cookiecutter](https://github.com/cookiecutter/cookiecutter)
2. Run Cookiecutter on this repo:
   ```bash
   pipx run cookiecutter gh:one-zero-eight/fastapi-template
   ```
3. Go to generated project and install dependencies with [Poetry](https://python-poetry.org/docs/cli/#install)
   ```bash
   poetry install
   ```
4. Run [Ruff](https://docs.astral.sh/ruff/) formatting and linting:
   ```bash
   poetry run ruff format
   poetry run ruff check --fix
   ```
5. Generate `settings.schema.yaml`:
   ```bash
   poetry run python scripts/generate_settings_schema.py
   ```

# How to update dependencies

## Project dependencies

1. Run `poetry update` to update all dependencies (it may update nothing, so double-check)
2. Run `poetry show --outdated --all` to check for outdated dependencies
3. Run `poetry add <package>@latest [--group <group>]` to add a new dependency if needed
4. Also, copy `mongo` and `sql` dependency groups from [pyproject.toml](pyproject.toml)
   to <a href="{{ cookiecutter.project_slug }}/pyproject.toml.jinja">pyproject.toml.jinja</a>

## Pre-commit hooks

1. Run `poetry run pre-commit autoupdate`

Also, Dependabot will help you to keep your dependencies up-to-date, see [dependabot.yml](.github/dependabot.yml).
