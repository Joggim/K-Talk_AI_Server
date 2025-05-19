from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# Wav2Vec2.0 기반 STT 함수 임포트
from app.services.stt_service import transcribe_wav2vec, transcribe_whisper, transcribe_google_stt

router = APIRouter()

@router.post("/stt/wav2vec2")
async def transcribe(file: UploadFile = File(...)):
    try:
        text = await transcribe_wav2vec(file)
        return JSONResponse(content={"transcription": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stt/whisper")
async def transcribe(file: UploadFile = File(...)):
    try:
        text = await transcribe_whisper(file)
        return JSONResponse(content={"transcription": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/stt/google-stt")
async def transcribe_endpoint(file: UploadFile = File(...)):
    try:
        text = await transcribe_google_stt(file)
        return JSONResponse(content={"transcription": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))