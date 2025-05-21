from fastapi import FastAPI
from app.api.routes import stt_api
from app.api.routes import feedback_api
from app.api.routes import talkbot_api
from app.api.routes import errortype_api
from app.api.routes import recommendation_api



from app.api.routes import tts_api
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

app = FastAPI()

# 라우터 등록
app.include_router(stt_api.router)
app.include_router(feedback_api.router)
app.include_router(talkbot_api.router)
app.include_router(errortype_api.router)
app.include_router(tts_api.router)
app.include_router(recommendation_api.router)

@app.get("/")
def root():
    return {"message": "K-Talk AI 서버에 오신 것을 환영합니다!"}

# 실행용 코드 추가
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
