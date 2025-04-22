from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.talkbot_service import get_bot_reply
from app.services.stt_service import transcribe_audio_file_wav2vec, transcribe_audio_file_whisper
from app.services.grammar_service import get_grammar_feedback
from app.services.pronunciation_service import evaluate_pronunciation_with_index

router = APIRouter()

@router.post("/chat/feedback")
async def chat_message(
    file: UploadFile = File(...),
    transcription: str = Form(...)
):
    """
    사용자 음성 입력을 받아 피드백 생성
    """
    try:
        raw_transcription = await transcribe_audio_file_wav2vec(file)
        grammar_feedback = await get_grammar_feedback(transcription)
        pronunciation_feedback = evaluate_pronunciation_with_index(transcription, raw_transcription)
        pronunciation_errors = pronunciation_feedback.get("pronunciationErrors")
        
        messages = [
            {
                "content": transcription,
                "isFeedback": bool(grammar_feedback.get("isFeedback") or pronunciation_errors),
                "feedback": {
                    "grammar": grammar_feedback,
                    "pronunciation": {
                        "pronunciationErrors": pronunciation_errors
                    }
                },
                "modelAudioUrl": "audio_path" # tts 구현하고 연결
            },
        ]

        return messages
    except Exception as e:
        print("🔥 Chat Response Error:", e) 
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/reply")
async def chat_response(sentence: str = Form(...)):
    """
    텍스트 입력을 받아 챗봇 응답을 생성
    """
    try:
        reply = get_bot_reply(sentence)
        return {
            "korean": reply.get("korean", "알겠습니다!"),
            "translation": reply.get("translation", "Okay!"),
            "modelAudioUrl": "audio_path" # tts 구현하고 연결
        }
    except Exception as e:
        print("🔥 Chat Response Error:", e) 
        raise HTTPException(status_code=500, detail=str(e))
