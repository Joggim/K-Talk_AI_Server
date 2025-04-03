import whisper
import shutil
import os
from fastapi import UploadFile

# Whisper 모델 초기화 (전역 로딩)
model = whisper.load_model("tiny")

async def transcribe_audio_file(file: UploadFile) -> str:
    temp_file_path = "temp_audio.wav"

    # 파일 저장
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # STT 수행
    result = model.transcribe(temp_file_path)

    # 임시 파일 삭제
    os.remove(temp_file_path)

    return result['text']