from fastapi import APIRouter
from IPAkor.transcription import UniTranscript
from app.api.schemas.ipa import IPARequest, IPAResponse

router = APIRouter()
t = UniTranscript()

@router.post("/ipa", response_model=IPAResponse)
async def convert_ipa(req: IPARequest):
    ipa = t.transcribator(req.text)
    return {"ipa": ipa}