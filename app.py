from flask import Flask, request, jsonify
import whisper

app = Flask(__name__)

# Whisper 모델 로드
model = whisper.load_model("tiny")

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    audio_file = request.files['file']
    audio_path = "temp_audio.wav"
    audio_file.save(audio_path)  # 파일 저장

    # 음성 파일에서 텍스트 추출
    result = model.transcribe(audio_path)
    
    return jsonify({"transcription": result['text']})

if __name__ == '__main__':
    app.run(debug=True)
