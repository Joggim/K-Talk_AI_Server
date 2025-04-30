from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.tts_service import synthesize_text_to_speech

router = APIRouter()

class TtsRequest(BaseModel):
    text: str

@router.post("/tts")
async def tts_endpoint(request: TtsRequest):
    audio_stream = synthesize_text_to_speech(request.text)
    return StreamingResponse(
    audio_stream,
    media_type="audio/mpeg",
    headers={
        "Content-Disposition": "inline; filename=output.mp3"
    }
)
