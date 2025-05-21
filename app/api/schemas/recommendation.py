from pydantic import BaseModel

class RecommendationRequest(BaseModel):
    error_type: str
