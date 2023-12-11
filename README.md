# FastAPI Template

# How to run

1. Install Poetry
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
   poetry run python -m src.api --use-colors --proxy-headers --forwarded-allow-ips=*
   ```
   Or
   ```bash
   poetry run uvicorn src.api.app:app --use-colors --proxy-headers --forwarded-allow-ips=*
   ```
