from pydantic import BaseModel
from typing import List

class PhonemeDiff(BaseModel):
    correctPhonemes: List[str]
    userPhonemes: List[str]
    diff: List[str]

class EvaluationResponse(BaseModel):
    reference: str
    userText: str
    errorDetails: PhonemeDiff