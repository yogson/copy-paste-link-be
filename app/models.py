from pydantic import BaseModel, Field


class TextItem(BaseModel):
    text: str
    one_time: bool = Field(..., alias='oneTime')
    short_code: bool = Field(False, alias='shortCode')  # Default value set to False

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
