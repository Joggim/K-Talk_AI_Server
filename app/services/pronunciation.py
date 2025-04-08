from typing import List, Dict, Any, Set
from difflib import SequenceMatcher
from app.services.g2p import convert_to_phonemes
from app.services.phonology import apply_phonological_variants

def phoneme_diff(correct: List[str], user: List[str], allowed_variants: Set[str]) -> Dict[str, Any]:
    diff = []

    matcher = SequenceMatcher(None, correct, user)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        for i, j in zip(range(i1, i2), range(j1, j2)):
            correct_ph = correct[i] if i < len(correct) else ""
            user_ph = user[j] if j < len(user) else ""

            # 허용 발음으로 간주되면 skip
            test_pron = correct[:]
            test_pron[i] = user_ph
            if ''.join(test_pron) in allowed_variants:
                continue

            diff.append(f"{user_ph or '(없음)'} → {correct_ph or '(없음)'}")

        # 길이 차이로 인해 발생하는 삽입/삭제
        for i in range(i2 - i1, j2 - j1):
            if j1 + i < len(user):
                p = user[j1 + i]
                test_pron = correct + [p]
                if ''.join(test_pron) not in allowed_variants:
                    diff.append(f"{p} → (없음)")

        for i in range(j2 - j1, i2 - i1):
            if i1 + i < len(correct):
                p = correct[i1 + i]
                test_pron = user + [p]
                if ''.join(test_pron) not in allowed_variants:
                    diff.append(f"(없음) → {p}")

    return {
        "correctPhonemes": correct,
        "userPhonemes": user,
        "diff": diff
    }

def evaluate_pronunciation(reference: str, user_text: str) -> Dict[str, Any]:
    """
    발음 평가 메인 함수
    - reference: 정답 문장
    - user_text: Whisper STT 결과
    """
    correct_phonemes = convert_to_phonemes(reference)
    user_phonemes = convert_to_phonemes(user_text)

    allowed_variants = apply_phonological_variants(''.join(correct_phonemes))

    return {
        "reference": reference,
        "userText": user_text,
        "errorDetails": phoneme_diff(correct_phonemes, user_phonemes, allowed_variants)
    }