from pydantic import BaseModel

class IPARequest(BaseModel):
    text: str

class IPAResponse(BaseModel):
    ipa: str