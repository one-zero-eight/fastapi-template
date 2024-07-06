from typing import cast

from beanie import Document, View

from src.storages.mongo.users import User

document_models = cast(
    list[type[Document] | type[View] | str],
    [User],
)
