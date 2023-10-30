from src.storages.sqlalchemy.models.base import Base
import src.storages.sql.models.__mixin__  # noqa: F401, E402

# Add all models here
from src.storages.sqlalchemy.models.some_model_in_plural import SomeModelInSingle

__all__ = ["Base", "SomeModelInSingle"]
