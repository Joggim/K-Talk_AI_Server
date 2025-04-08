from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.pronunciation import evaluate_pronunciation

router = APIRouter()

class PronunciationRequest(BaseModel):
    reference: str       # 예: "삼겹살을 좋아해"
    user_text: str       # 예: "삼꼅쌀을 조아해"

@router.post("/evaluate")
async def evaluate_pronunciation_route(body: PronunciationRequest):
    try:
        result = evaluate_pronunciation(body.reference, body.user_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))