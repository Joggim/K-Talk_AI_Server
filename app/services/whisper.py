import shutil
import os


import torch
import soundfile as sf
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from fastapi import HTTPException, UploadFile
from pydub import AudioSegment  # 추가
import tempfile

# 모델 및 프로세서 초기화 (전역 로딩)
model_name = "kresnik/wav2vec2-large-xlsr-korean"
processor = Wav2Vec2Processor.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name)
model.eval()




async def transcribe_audio_file_wav2vec(file: UploadFile) -> str:
    try:
        # 1. 업로드된 파일을 임시 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".original") as tmp_original:
            shutil.copyfileobj(file.file, tmp_original)
            original_path = tmp_original.name

        # 2. 원본 오디오 → wav로 변환 (pydub 사용)
        temp_wav_path = original_path + ".wav"
        audio = AudioSegment.from_file(original_path)
        audio = audio.set_frame_rate(16000).set_channels(1)  # mono + 16kHz
        audio.export(temp_wav_path, format="wav")

        # 3. 오디오 읽기
        audio_input, sr = sf.read(temp_wav_path)

        if len(audio_input.shape) > 1:
            audio_input = audio_input.mean(axis=1)

        # 4. 모델 입력
        input_values = processor(
            audio_input,
            sampling_rate=16000,
            return_tensors="pt",
            padding=True
        ).input_values

        with torch.no_grad():
            logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)

        transcription = processor.batch_decode(predicted_ids)
        return transcription[0]

    finally:
        # 5. 파일 정리
        for path in [original_path, temp_wav_path]:
            if os.path.exists(path):
                os.remove(path)
