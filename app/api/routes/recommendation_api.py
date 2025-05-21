from fastapi import APIRouter
from app.api.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import generate_recommendation_sentences

router = APIRouter()

@router.post("/recommend-sentences")
async def recommend_sentences(request: RecommendationRequest):
    results = generate_recommendation_sentences(tag=request.error_type, n=50)
    return results
