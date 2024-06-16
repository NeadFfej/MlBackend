from typing import Literal

from pydantic import Field, BaseModel
from fastapi import Query


# Base Models Data
class PublickModelData(BaseModel):
    model: Literal[""]
    

class PersonalModelData(PublickModelData):
    pass


# Create CRUD Models Data
class CreatePublickModelData(PublickModelData):
    pass


class CreatePersonalModelData(PersonalModelData):
    pass
