from pydantic import BaseModel

class ErrorRequest(BaseModel):
    target: str
    user: str
    prev: str
    next: str
    jamo_index_in_syllable: int