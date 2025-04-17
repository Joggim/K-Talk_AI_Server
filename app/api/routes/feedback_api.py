from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.pronunciation_service import evaluate_pronunciation_with_index
from app.services.stt_service import transcribe_audio_file_wav2vec
from app.services.grammar_service import get_grammar_feedback

router = APIRouter()

class PronunciationRequest(BaseModel):
    reference: str       # 예: "삼겹살을 좋아해"
    user_text: str       # 예: "삼꼅쌀을 조아해"

@router.post("/feedback/pronunciation")
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
    
class GrammarRequest(BaseModel):
    text: str  # 사용자 발화 (STT 결과)

@router.post("/feedback/grammar")
async def get_grammar_feedback(req: GrammarRequest):
    try:
        feedback = get_grammar_feedback(req.text)
        return {"grammarFeedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))