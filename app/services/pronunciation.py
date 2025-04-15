from typing import List, Dict, Any, Set, Optional
from difflib import SequenceMatcher
from app.services.g2p import convert_to_phonemes, convert_to_phonemes_with_mapping
from app.services.phonology import apply_phonological_variants
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

def is_ignorable_phoneme(ph: str) -> bool:
    return ph in string.punctuation or ph == " " or ph == "(없음)"

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
    seen_indices = set()

    matcher = SequenceMatcher(None, correct, user)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        # 교체
        for i, j in zip(range(i1, i2), range(j1, j2)):
            correct_ph = correct[i] if i < len(correct) else ""
            user_ph = user[j] if j < len(user) else ""

            test_pron = correct[:]
            test_pron[i] = user_ph
            if test_pron == correct or ''.join(test_pron) in allowed_variants:
                continue

            if is_ignorable_phoneme(user_ph) or is_ignorable_phoneme(correct_ph):
                continue

            diff.append({"wrong": user_ph or "(없음)", "correct": correct_ph or "(없음)"})

            if i < len(correct_phoneme_to_char_index):
                char_idx = correct_phoneme_to_char_index[i]
                if char_idx not in char_errors:
                    correct_char = correct_chars[char_idx] if char_idx < len(correct_chars) else "(없음)"
                    if is_ignorable_phoneme(correct_char):
                        continue
                    user_char = user_chars[char_idx] if char_idx < len(user_chars) else "(없음)"
                    char_errors[char_idx] = {
                        "wrong": user_char,
                        "correct": correct_char,
                        "index": char_idx
                    }

        # 삽입
        for k in range(i2 - i1, j2 - j1):
            j = j1 + k
            if j < len(user):
                user_ph = user[j]
                test_pron = correct + [user_ph]
                if test_pron == correct or ''.join(test_pron) in allowed_variants:
                    continue

                if is_ignorable_phoneme(user_ph):
                    continue

                diff.append({"wrong": user_ph, "correct": "(없음)"})
                nearest_i = i1 + k - 1 if (i1 + k - 1) < len(correct_phoneme_to_char_index) else len(correct_chars) - 1
                if 0 <= nearest_i < len(correct_phoneme_to_char_index):
                    char_idx = correct_phoneme_to_char_index[nearest_i]
                    if char_idx not in char_errors:
                        correct_char = correct_chars[char_idx] if char_idx < len(correct_chars) else "(없음)"
                        if is_ignorable_phoneme(correct_char):
                            continue
                        user_char = user_chars[char_idx] if char_idx < len(user_chars) else "(없음)"
                        char_errors[char_idx] = {
                            "wrong": user_char,
                            "correct": correct_char,
                            "index": char_idx
                        }

        # 삭제
        for k in range(j2 - j1, i2 - i1):
            i = i1 + k
            if i < len(correct):
                correct_ph = correct[i]
                test_pron = user + [correct_ph]
                if test_pron == correct or ''.join(test_pron) in allowed_variants:
                    continue

                if is_ignorable_phoneme(correct_ph):
                    continue

                diff.append({"wrong": "(없음)", "correct": correct_ph})
                if i < len(correct_phoneme_to_char_index):
                    char_idx = correct_phoneme_to_char_index[i]
                    if char_idx not in char_errors:
                        correct_char = correct_chars[char_idx] if char_idx < len(correct_chars) else "(없음)"
                        if is_ignorable_phoneme(correct_char):
                            continue
                        user_char = user_chars[char_idx] if char_idx < len(user_chars) else "(없음)"
                        char_errors[char_idx] = {
                            "wrong": user_char,
                            "correct": correct_char,
                            "index": char_idx
                        }

    # 문자 단위 비교
    all_char_indices = set(correct_phoneme_to_char_index + user_phoneme_to_char_index)

    for char_index in all_char_indices:
        if char_index in seen_indices:
            continue

        correct_char = correct_chars[char_index] if char_index < len(correct_chars) else "(없음)"
        user_char = user_chars[char_index] if char_index < len(user_chars) else "(없음)"

        if is_ignorable_phoneme(correct_char):
            continue

        correct_ph_indices = [i for i, x in enumerate(correct_phoneme_to_char_index) if x == char_index]
        user_ph_indices = [i for i, x in enumerate(user_phoneme_to_char_index) if x == char_index]

        correct_sub = [correct[i] for i in correct_ph_indices if i < len(correct)]
        user_sub = [user[i] for i in user_ph_indices if i < len(user)]

        if correct_sub != user_sub:
            test_pron = correct[:]
            for i, ph in zip(correct_ph_indices, user_sub):
                if i < len(test_pron):
                    test_pron[i] = ph

            if test_pron == correct or ''.join(test_pron) in allowed_variants:
                continue

            seen_indices.add(char_index)
            if char_index not in char_errors:
                char_errors[char_index] = {
                    "wrong": user_char,
                    "correct": correct_char,
                    "index": char_index
                }

    return {
        "correctPhonemes": correct,
        "userPhonemes": user,
        "diff": diff,
        "pronunciationErrors": list(char_errors.values()),
        "passed": len(char_errors) == 0
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