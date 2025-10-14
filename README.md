# FastAPI Template

## About

This is the CookieCutter template for FastAPI ASGI application.
We use it in most of our projects. See structure at [{{ cookiecutter.project_slug }}]({{%20cookiecutter.project_slug%20}}/) and keep it synced with the generated project from this template. If you found something cozy to be added, something missing or not working, please report an issue or submit a pull request.

### Technologies

- [Python 3.13](https://www.python.org/downloads/) & [uv](https://docs.astral.sh/uv/)
- [FastAPI](https://fastapi.tiangolo.com/)
- Database and ORM: [MongoDB](https://www.mongodb.com/) & [Beanie](https://beanie-odm.dev/)
- Formatting and linting: [Ruff](https://docs.astral.sh/ruff/), [pre-commit](https://pre-commit.com/)
- Deployment: [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/),
  [GitHub Actions](https://github.com/features/actions)

## How to use?

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Run Cookiecutter on this repo:
   ```bash
   uvx cookiecutter gh:one-zero-eight/fastapi-template
   ```
3. Go to generated project and install dependencies with [uv](https://astral.sh/uv/)
   ```bash
   uv sync
   ```
4. Run [Ruff](https://docs.astral.sh/ruff/) formatting and linting:
   ```bash
   uv run ruff format
   uv run ruff check --fix
   ```
5. Generate `settings.schema.yaml`:
   ```bash
   uv run python scripts/generate_settings_schema.py
   ```
