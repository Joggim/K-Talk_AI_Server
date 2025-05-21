from fastapi import APIRouter
from app.api.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import generate_recommendation_sentences
from IPAkor.transcription import UniTranscript

router = APIRouter()
t = UniTranscript()

@router.post("/recommend-sentences")
async def recommend_sentences(request: RecommendationRequest):
    results = generate_recommendation_sentences(tag=request.error_type, n=50)
    
    for item in results:
        ipa = t.transcribator(item["content"])
        item["ipa"] = ''.join(ipa)
        
    return results
