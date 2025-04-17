from fastapi import APIRouter, Form, HTTPException
from app.services.talkbot_service import get_bot_reply

router = APIRouter()

@router.post("/chat-response")
async def chat_response(sentence: str = Form(...)):
    """
    텍스트 입력을 받아 챗봇 응답을 생성
    """
    try:
        reply = get_bot_reply(sentence)
        return {
            "korean": reply.get("korean", "알겠습니다!"),
            "translation": reply.get("translation", "Okay!")
        }
    except Exception as e:
        print("🔥 Chat Response Error:", e) 
        raise HTTPException(status_code=500, detail=str(e))