from pydantic import BaseModel, Field

class ErrorRequest(BaseModel):
    target: str = Field(..., alias="target")
    user: str = Field(..., alias="user")
    prev: str = Field(..., alias="prev")
    next: str = Field(..., alias="next")
    jamo_index_in_syllable: int = Field(..., alias="jamoIndex")

    class Config:
        allow_population_by_field_name = True


class ErrorResponse(BaseModel):
    target: str
    user: str
    prev: str
    next: str
    jamoIndex: int
    errorType: str