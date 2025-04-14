from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.pronunciation import evaluate_pronunciation_with_index, evaluate_pronunciation
from app.services.transcribe import transcribe_audio_file_wav2vec

router = APIRouter()

class PronunciationRequest(BaseModel):
    reference: str       # 예: "삼겹살을 좋아해"
    user_text: str       # 예: "삼꼅쌀을 조아해"

@router.post("/evaluate")
async def evaluate_audio(
    file: UploadFile = File(...),
    reference: str = Form(...)
):
    
    try:
        # 1. STT (음성 → 텍스트)
        user_text = await transcribe_audio_file_wav2vec(file)

        # 2. 발음 평가 결과 반환
        return evaluate_pronunciation_with_index(reference, user_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/evaluate1")
async def evaluate_pronunciation_route(body: PronunciationRequest):
    try:
        result = evaluate_pronunciation(body.reference, body.user_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))