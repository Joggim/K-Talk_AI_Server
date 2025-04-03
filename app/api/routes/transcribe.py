from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.whisper import transcribe_audio_file

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        text = await transcribe_audio_file(file)
        return JSONResponse(content={"transcription": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))