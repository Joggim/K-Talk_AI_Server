import os
import torch
import torch.nn as nn
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../models/mlp_pronunciation_classifier.pt")
ENCODER_PATH = os.path.join(BASE_DIR, "../models/label_encoder.pkl")

# 🔡 자모 인코딩 함수
def encode_jamo(jamo):
    jamo_to_idx = {
        '': 0, 'ㄱ': 1, 'ㄲ': 2, 'ㄴ': 3, 'ㄷ': 4, 'ㄸ': 5, 'ㄹ': 6,
        'ㅁ': 7, 'ㅂ': 8, 'ㅃ': 9, 'ㅅ': 10, 'ㅆ': 11, 'ㅇ': 12,
        'ㅈ': 13, 'ㅉ': 14, 'ㅊ': 15, 'ㅋ': 16, 'ㅌ': 17, 'ㅍ': 18, 'ㅎ': 19,
        'ㅏ': 20, 'ㅐ': 21, 'ㅑ': 22, 'ㅓ': 23, 'ㅕ': 24, 'ㅗ': 25,
        'ㅛ': 26, 'ㅜ': 27, 'ㅠ': 28, 'ㅡ': 29, 'ㅣ': 30
    }
    return jamo_to_idx.get(jamo, 0)

# 🧠 MLP 모델 정의
class MLPClassifier(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, output_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.fc = nn.Sequential(
            nn.Linear(embedding_dim * 5, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        emb = self.embedding(x)
        flat = emb.view(x.size(0), -1)
        return self.fc(flat)

# 📦 하이퍼파라미터 및 모델 로드
VOCAB_SIZE = 52
EMBED_DIM = 64
HIDDEN_DIM = 128
OUTPUT_DIM = 7

model = MLPClassifier(VOCAB_SIZE, EMBED_DIM, HIDDEN_DIM, OUTPUT_DIM)
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu")))
model.eval()

label_encoder = joblib.load(ENCODER_PATH)

def predict_error_type(target, user, prev, next_, jamo_index_in_syllable):
    encoded = torch.tensor([[
        encode_jamo(target),
        encode_jamo(user),
        encode_jamo(prev),
        encode_jamo(next_),
        jamo_index_in_syllable
    ]], dtype=torch.long)
    with torch.no_grad():
        output = model(encoded)
        pred_idx = output.argmax(1).item()