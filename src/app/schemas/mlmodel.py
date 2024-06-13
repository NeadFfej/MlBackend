from typing import Literal

from pydantic import Field, BaseModel
from fastapi import Query


# Base Models Data
class PublickModelData(BaseModel):
    size: Literal["small", "medium", "large"]
    iterations: Literal[10, 100, 1000]
    
    @staticmethod # Bug fix with content_type, UploadFile and Depends in FastApi
    def query_validator(
        size: Literal["small", "medium", "large"] = Query(),
        iterations: Literal["10", "100", "1000"] = Query(),
    ):
        return PublickModelData(size=size, iterations=int(iterations))


class PersonalModelData(PublickModelData):
    iterations: int = Field(ge=1, le=1000)


# Create CRUD Models Data
class CreatePublickModelData(PublickModelData):
    pass


class CreatePersonalModelData(PersonalModelData):
    pass
