from typing import Literal

from pydantic import Field, BaseModel
from fastapi import Query


# Base Models Data
class PublickModelData(BaseModel):
    name: Literal[
        "train_data_50for",
        "train_data_100for",
        "train_data_200for"
    ]
    

class PersonalModelData(PublickModelData):
    pass


# Create CRUD Models Data
class CreatePublickModelData(PublickModelData):
    pass


class CreatePersonalModelData(PersonalModelData):
    pass
