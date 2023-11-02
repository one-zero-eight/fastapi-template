__all__ = [
    "CreateSomeScheme",
    "ViewSomeScheme",
    "UpdateSomeScheme",
]

from pydantic import BaseModel, ConfigDict


class CreateSomeScheme(BaseModel):
    ...


class ViewSomeScheme(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )


class UpdateSomeScheme(BaseModel):
    ...


# Note: if some relation is needed, add it here
# from src.schemas.some_scheme2_in_plural import ViewSomeScheme2InPlural
# ViewSomeSchemeInSingle.model_rebuild()
