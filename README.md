# FastAPI Template

# How to run

1. Install [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
2. Install dependencies
    ```bash
   poetry install --no-root --with dev
   ```
3. Setup pre-commit hooks
    ```bash
   poetry run pre-commit install --install-hooks -t pre-commit -t commit-msg
   ```
4. Run app
   ```bash
   poetry run python -m src.api
   ```
   Or
   ```bash
   poetry run uvicorn src.api.app:app --use-colors --proxy-headers --forwarded-allow-ips=*
   ```

# How to update

## Project dependencies

1. Run `poetry update` to update all dependencies
2. Run `poetry show --outdated` to check for outdated dependencies
3. Run `poetry add <package>@latest` to add a new dependency if needed

## Pre-commit hooks

1. Run `poetry run pre-commit autoupdate`