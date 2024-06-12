from typing import Literal

from pydantic import field_validator, Field, BaseModel


# Base Models Data
class PublickModelData(BaseModel):
    size: Literal["small", "medium", "large"]
    # Bug fix with content_type, UploadFile and Depends in FastApi
    iterations: Literal[10, 100, 1000] | Literal["10", "100", "1000"]
    
    @field_validator("iterations", mode="before")
    def process_text(cls, v) -> int:
        return int(v)


class PersonalModelData(PublickModelData):
    iterations: int = Field(ge=1, le=1000)


# Create CRUD Models Data
class CreatePublickModelData(PublickModelData):
    pass


class CreatePersonalModelData(PersonalModelData):
    pass
