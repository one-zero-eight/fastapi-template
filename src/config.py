import os
from pathlib import Path

from src.config_schema import Settings

settings_path = os.getenv("SETTINGS_PATH")
if settings_path is None:
    settings_path = "settings.yaml"
settings: Settings = Settings.from_yaml(Path(settings_path))
