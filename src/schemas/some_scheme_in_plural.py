from pydantic import BaseModel


class CreateSomeSchemeInSingle(BaseModel):
    ...


class ViewSomeSchemeInSingle(BaseModel):
    ...


class UpdateSomeSchemeInSingle(BaseModel):
    ...

# Note: if some relation is needed, add it here
# from src.schemas.some_scheme2_in_plural import ViewSomeScheme2InPlural
# ViewSomeSchemeInSingle.model_rebuild()
