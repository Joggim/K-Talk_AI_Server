from pydantic import BaseModel

class PronunciationRequest(BaseModel):
    reference: str       # 예: "삼겹살을 좋아해"
    user_text: str       # 예: "삼꼅쌀을 조아해"

class GrammarRequest(BaseModel):
    text: str  # 사용자 발화 (STT 결과)