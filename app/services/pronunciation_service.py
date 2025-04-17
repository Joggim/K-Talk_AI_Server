from typing import List, Dict, Any, Set, Optional
from difflib import SequenceMatcher
from app.services.g2p_service import convert_to_phonemes
from app.services.phonology_service import apply_phonological_variants
import string

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
 
def convert_to_phonemes_with_mapping(text: str):
    phonemes = []
    mapping = []  # phoneme index → 글자 index
    chars = list(text)

    for idx, char in enumerate(chars):
        phs = convert_to_phonemes(char)
        phonemes.extend(phs)
        mapping.extend([idx] * len(phs))  # 각 음소는 어떤 글자에서 왔는지

    return phonemes, mapping, chars  # char 리스트도 같이 리턴


def phoneme_diff_with_index(
    correct: List[str],
    user: List[str],
    allowed_variants: Set[str],
    correct_phoneme_to_char_index: Optional[List[int]] = None,
    correct_chars: Optional[List[str]] = None,
    user_phoneme_to_char_index: Optional[List[int]] = None,
    user_chars: Optional[List[str]] = None
) -> Dict[str, Any]:
    diff = []
    char_errors = []
    seen_indices = set()

    matcher = SequenceMatcher(None, correct, user)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        for i, j in zip(range(i1, i2), range(j1, j2)):
            correct_ph = correct[i] if i < len(correct) else ""
            user_ph = user[j] if j < len(user) else ""

            test_pron = correct[:]
            test_pron[i] = user_ph
            if ''.join(test_pron) in allowed_variants:
                continue

            # 음소 차이 기록
            diff.append(f"{user_ph or '(없음)'} → {correct_ph or '(없음)'}")

            # 글자 오류 기록 (옵션이 있을 경우만)
            if correct_phoneme_to_char_index and correct_chars and user_phoneme_to_char_index and user_chars:
                char_index = correct_phoneme_to_char_index[i] if i < len(correct_phoneme_to_char_index) else -1
                if char_index not in seen_indices:
                    correct_char = correct_chars[char_index] if char_index < len(correct_chars) else "(없음)"
                    if correct_char not in string.punctuation:  # 문장부호 제외
                        seen_indices.add(char_index)
                        char_errors.append({
                            "wrong": user_chars[user_phoneme_to_char_index[j]] if j < len(user_phoneme_to_char_index) else "(없음)",
                            "correct": correct_char,
                            "index": char_index
                        })

        # 삽입/삭제 처리
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

                # 글자 오류 기록 (삭제의 경우)
                if correct_phoneme_to_char_index and correct_chars:
                    char_index = correct_phoneme_to_char_index[i1 + i]
                    if char_index not in seen_indices:
                        correct_char = correct_chars[char_index] if char_index < len(correct_chars) else "(없음)"
                        if correct_char not in string.punctuation:  # 문장부호 제외
                            seen_indices.add(char_index)
                            char_errors.append({
                                "wrong": "(없음)",
                                "correct": correct_char,
                                "index": char_index
                            })

    return {
        "correctPhonemes": correct,
        "userPhonemes": user,
        "diff": diff,
        "pronunciationErrors": char_errors
    }
    
def evaluate_pronunciation_with_index(reference: str, user_text: str) -> Dict[str, Any]:
    correct_phonemes, correct_mapping, correct_chars = convert_to_phonemes_with_mapping(reference)
    user_phonemes, user_mapping, user_chars = convert_to_phonemes_with_mapping(user_text)

    allowed_variants = apply_phonological_variants(''.join(correct_phonemes))

    result = phoneme_diff_with_index(
        correct=correct_phonemes,
        user=user_phonemes,
        allowed_variants=allowed_variants,
        correct_phoneme_to_char_index=correct_mapping,
        correct_chars=correct_chars,
        user_phoneme_to_char_index=user_mapping,
        user_chars=user_chars
    )

    return {
        "reference": reference,
        "userText": user_text,
        "errorDetails": {
            "correctPhonemes": result["correctPhonemes"],
            "userPhonemes": result["userPhonemes"],
            "diff": result["diff"]
        },        
        "pronunciationErrors": result["pronunciationErrors"],
        "passed": len(result["pronunciationErrors"]) == 0
    }