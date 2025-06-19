# K-Talk AI

**K-Talk**은 **외국인 한국어 학습자를 위한 음성 인식 및 AI 기반 발음 교정 및 회화 연습 서비스**입니다. K-Talk AI 서버는 외국인 한국어 학습자를 위한 음성 기반 피드백 서비스를 지원하는 AI 처리 서버입니다.
FastAPI 기반으로 구성되어 있으며, Spring Boot 기반의 메인 서버와 통신하여 STT, TTS, 발음 오류 분석, 문장 추천, 문법 피드백 등의 기능을 제공합니다.
> 전체 프로젝트 설명은 [K-Talk 프로젝트 소개 레포지토리](https://github.com/Joggim/team-26-joggim)에서 확인하실 수 있습니다.

<br>

## 📌 주요 기능

- 사용자 발음 STT (wav2vec2 + g2pk)
- 텍스트 TTS (Google Text-to-Speech)
- 발음 오류 분석 및 rule/MLP 기반 오류 유형 분류
- 사용자 맞춤 문장 추천 (GPT 기반)
- 사용자 입력 문법 피드백 및 챗봇 응답

<br>

## 🛠️ 기술 스택

| 분류        | 사용 기술                        |
| --------- | ---------------------------- |
| Language  | Python 3.10                  |
| Framework | FastAPI                      |
| STT       | wav2vec2 + g2pk              |
| TTS       | Google Cloud TTS             |
| 오류 분석     | Rule-based + PyTorch MLP     |
| 추천        | GPT-4o                        |
| 배포        | Docker                       |
| 문서화       | FastAPI Swagger UI (`/docs`) |


<br>

## 📁 프로젝트 구조

```
.
├── app/
│   ├── api/                  # FastAPI 라우터
│   ├── services/             # STT, TTS, 오류 분석, 추천 등 기능별 서비스
│   ├── models/               # 학습된 모델 로딩
│   ├── utils/                
│   └── __init__.py
├── main.py                  
├── Dockerfile                # 컨테이너 실행 설정
├── requirements.txt          
├── .env                      # 환경변수 설정


```

<br>

## ⚙️ 실행 방법 (Docker로 실행)

### 1. `.env` 파일 생성

루트 디렉토리에 `.env` 파일을 생성하고 아래와 같이 환경변수를 설정합니다:

```dotenv
OPENAI_API_KEY=your-openai-api-key
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
```
- `OPENAI_API_KEY L` :OpenAI GPT API 호출을 위한 키 (ex. 발음 오류 분류, 피드백 생성 등)
- `GOOGLE_APPLICATION_CREDENTIALS ` : Google Cloud Speech-to-Text 사용 시 필요한 서비스 계정 인증 키 JSON 파일 경로.
   일반적으로 credentials.json

> ⚠️ GOOGLE_APPLICATION_CREDENTIALS는 Google Cloud Console에서 발급한 서비스 계정 키 파일입니다.
> 해당 파일(credentials.json)을 프로젝트 루트에 두고, 콘솔에서 다음 경로에서 발급받아야 합니다:
- Google: https://console.cloud.google.com/apis/credentials
    - OAuth 또는 STT용 서비스 계정 키 생성 후 JSON 다운로드
- OpenAI: https://platform.openai.com/api-keys
    - 개인 계정의 API 키 생성 후 .env에 복사

### 2. Docker 이미지 빌드
```bash
docker build -t ktalk-ai_server .
```

### 3. Docker 컨테이너 실행
```bash
docker run --env-file .env -p 8000:8000 ktalk-ai-server
```
> 실행 후 `http://localhost:8080`에서 API에 접근할 수 있습니다.

### ⚠️ Docker 실행 주의 사항
- Docker 엔진이 실행 중이어야 함
  - Windows/macOS 사용자는 Docker Desktop 실행 필요
  - Linux 사용자는 sudo systemctl start docker 등으로 도커 데몬 실행


<br>

## 🔌 주요 API

| 분류      | 메서드 | 경로                                              | 설명 |
|---------|--------|-------------------------------------------------|------|
| 🔊 STT | POST | `/stt/wave2vec2`                                   | 음성 파일 → 텍스트 변환 |
|         | POST | `/stt/google-stt`               | 사용자음성 -> 채팅변환 |
| 🗣️ TTS   |POST | `/tts`                   | 텍스트 → Google TTS 음성 생성 |
| 🧪 발음 분석| POST | `/feedback/pronunciation`                    | 정답 vs 사용자 발음 비교, 오류 리턴 |
| ✏️ 문법 분석| POST | `/feedback/grammar`                               | 사용자발화 문법 검증 |
| 💬 챗봇 응답| POST | `/chat/reply`                            |텍스트 입력을 받아 응답 생성 |
| ❗ 오류 분류 | POST |  `/classify`                      | 자모 벡터 입력 → 오류 유형 예측 |
|  📘 문장 추천 |POST | `/recommend-sentence` | 오류 유형 태그 입력 → 문장 추천 |
|🔤 IPA 변환|	POST|	`/ipa`|	텍스트 입력 → IPA 변환|
> 🔧 전체 API 요청/응답 상세는 Swagger UI(`/swagger-ui/index.html`)에서 확인할 수 있습니다. (서버 실행 시 접근 가능)

<br>

## 🛰️ 외부 API 및 모델

|서비스/API|	설명 |	사용 목적  |	링크      |                                       
|---------|--------|-------------------------------------------------|------|
| Google Cloud Text-to-Speech | 텍스트를 자연스러운 음성으로 합성하는 클라우드 API |학습문장 모범 발음 생성 |https://cloud.google.com/text-to-speech?hl=ko |
| Google Cloud Speech-to-Text | 한국어 음성을 텍스트로 바꿔주는 모델 |채팅 STT 기능 구현 |https://cloud.google.com/speech-to-text?hl=ko |
| OpenAI GPT-4o | 대화 응답, 문법 피드백, 문장 추천에 사용되는 자연어 처리 모델 |챗봇 응답 생성, 추천 문장 생성 |https://openai.com |
| HuggingFace Wav2Vec2 | 한국어 음성 인식용 사전학습 모델 |STT 기능 구현 | https://huggingface.co/docs/transformers/model_doc/wav2vec2|

