import os
import shutil
import tempfile

import torch
import soundfile as sf
import whisper
from fastapi import HTTPException, UploadFile
from pydub import AudioSegment
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from google.cloud import speech

# Wav2Vec2 모델 및 프로세서 초기화
wav2vec_model_name = "kresnik/wav2vec2-large-xlsr-korean"
wav2vec_processor = Wav2Vec2Processor.from_pretrained(wav2vec_model_name)
wav2vec_model = Wav2Vec2ForCTC.from_pretrained(wav2vec_model_name)
wav2vec_model.eval()

# Whisper 모델 초기화
whisper_model = whisper.load_model("base")

def convert_to_wav_linear16(input_path: str, output_path: str):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(output_path, format="wav")

async def transcribe_wav2vec(file: UploadFile) -> str:
    try:
        # 1. 업로드된 파일을 임시 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".original") as tmp_original:
            shutil.copyfileobj(file.file, tmp_original)
            original_path = tmp_original.name

        # 2. 원본 오디오 → wav로 변환 (pydub 사용)
        temp_wav_path = original_path + ".wav"
        convert_to_wav_linear16(original_path, temp_wav_path)

        # 3. 오디오 읽기
        audio_input, sr = sf.read(temp_wav_path)
        if len(audio_input.shape) > 1:
            audio_input = audio_input.mean(axis=1)

        # 4. 모델 입력
        input_values = wav2vec_processor(
            audio_input,
            sampling_rate=16000,
            return_tensors="pt",
            padding=True
        ).input_values

        with torch.no_grad():
            logits = wav2vec_model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)

        transcription = wav2vec_processor.batch_decode(predicted_ids)
        return transcription[0]

    finally:
        # 5. 파일 정리
        for path in [original_path, temp_wav_path]:
            if os.path.exists(path):
                os.remove(path)


async def transcribe_whisper(file: UploadFile) -> str:
    temp_file_path = "temp_audio.wav"

    # 파일 저장
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # STT 수행 (언어 명시!)
        result = whisper_model.transcribe(
            temp_file_path,
            temperature=0.0,
            language="ko"
        )
        return result["text"]
    finally:
        # 임시 파일 삭제
        os.remove(temp_file_path)

async def transcribe_google_stt(file: UploadFile) -> str:
    try:
        # 1. 임시 파일 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".input") as tmp:
            shutil.copyfileobj(file.file, tmp)
            input_path = tmp.name

        # 2. 변환
        converted_path = input_path + ".wav"
        convert_to_wav_linear16(input_path, converted_path)

        # 3. STT 요청
        client = speech.SpeechClient()

        with open(converted_path, "rb") as audio_file:
            audio_content = audio_file.read()

        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="ko-KR"
        )

        response = client.recognize(config=config, audio=audio)
        transcript = " ".join([r.alternatives[0].transcript for r in response.results])
        return transcript or "음성이 인식되지 않았습니다."

    finally:
        for path in [input_path, converted_path]:
            if os.path.exists(path):
                os.remove(path)