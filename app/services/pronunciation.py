from typing import List, Dict, Any, Set, Optional
from difflib import SequenceMatcher
from app.services.g2p import convert_to_phonemes, convert_to_phonemes_with_mapping
from app.services.phonology import apply_phonological_variants
import string
import hgtk

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

def phoneme_diff_with_index(
    correct: List[str],
    user: List[str],
    allowed_variants: Set[str],
    correct_chars: List[str],
    user_chars: List[str],
    correct_phoneme_to_char_index: List[int],
    user_phoneme_to_char_index: List[int]
) -> Dict[str, Any]:
    diff = []
    char_errors = {}

    matcher = SequenceMatcher(None, correct, user)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        # 교체된 부분
        for i, j in zip(range(i1, i2), range(j1, j2)):
            correct_ph = correct[i] if i < len(correct) else ""
            user_ph = user[j] if j < len(user) else ""

            test_pron = correct[:]
            test_pron[i] = user_ph
            if ''.join(test_pron) in allowed_variants:
                continue

            diff.append({"wrong": user_ph or "(없음)", "correct": correct_ph or "(없음)"})

            if i < len(correct_phoneme_to_char_index):
                char_idx = correct_phoneme_to_char_index[i]
                if char_idx not in char_errors:
                    char_errors[char_idx] = {
                        "wrong": user_chars[char_idx] if char_idx < len(user_chars) else correct_chars[char_idx],
                        "correct": correct_chars[char_idx],
                        "index": char_idx
                    }

        # user에만 있는 삽입
        for k in range(i2 - i1, j2 - j1):
            j = j1 + k
            if j < len(user):
                p = user[j]
                test_pron = correct + [p]
                if ''.join(test_pron) not in allowed_variants:
                    diff.append({"wrong": p, "correct": "(없음)"})

                    # 삽입된 경우에도 reference 기준 가장 가까운 index 사용
                    nearest_i = i1 + k - 1 if (i1 + k - 1) < len(correct_phoneme_to_char_index) else len(correct_chars) - 1
                    if 0 <= nearest_i < len(correct_phoneme_to_char_index):
                        char_idx = correct_phoneme_to_char_index[nearest_i]
                        if char_idx not in char_errors:
                            char_errors[char_idx] = {
                                "wrong": user_chars[char_idx] if char_idx < len(user_chars) else correct_chars[char_idx],
                                "correct": correct_chars[char_idx],
                                "index": char_idx
                            }

        # correct에만 있는 삭제
        for k in range(j2 - j1, i2 - i1):
            i = i1 + k
            if i < len(correct):
                p = correct[i]
                test_pron = user + [p]
                if ''.join(test_pron) not in allowed_variants:
                    diff.append({"wrong": "(없음)", "correct": p})

                    if i < len(correct_phoneme_to_char_index):
                        char_idx = correct_phoneme_to_char_index[i]
                        if char_idx not in char_errors:
                            char_errors[char_idx] = {
                                "wrong": user_chars[char_idx] if char_idx < len(user_chars) else correct_chars[char_idx],
                                "correct": correct_chars[char_idx],
                                "index": char_idx
                            }

    return {
        "correctPhonemes": correct,
        "userPhonemes": user,
        "diff": diff,
        "pronunciationErrors": list(char_errors.values()),
        "passed": len(diff) == 0
    }
    
def evaluate_pronunciation_with_index(reference: str, user_text: str) -> Dict[str, Any]:
    correct_phonemes, correct_mapping, correct_chars = convert_to_phonemes_with_mapping(reference)
    user_phonemes, user_mapping, user_chars = convert_to_phonemes_with_mapping(user_text)

    allowed_variants = apply_phonological_variants(''.join(correct_phonemes))
    print(allowed_variants)

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