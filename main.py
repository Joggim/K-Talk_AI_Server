from fastapi import FastAPI
from app.api.routes import stt_api
from app.api.routes import pronunciation

app = FastAPI()

# 라우터 등록
app.include_router(stt_api.router)
app.include_router(pronunciation.router)

@app.get("/")
def root():
    return {"message": "K-Talk AI 서버에 오신 것을 환영합니다!"}

# 실행용 코드 추가
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)