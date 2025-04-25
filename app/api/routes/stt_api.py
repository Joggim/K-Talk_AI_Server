from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# Wav2Vec2.0 기반 STT 함수 임포트
from app.services.stt_service import transcribe_audio_file_wav2vec, transcribe_audio_file_whisper

router = APIRouter()

@router.post("/stt/wav2vec2")
async def transcribe(file: UploadFile = File(...)):
    try:
        text = await transcribe_audio_file_wav2vec(file)
        return JSONResponse(content={"transcription": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stt/whisper")
async def transcribe(file: UploadFile = File(...)):
    try:
        text = await transcribe_audio_file_whisper(file)
        return JSONResponse(content={"transcription": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))