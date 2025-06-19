from typing import List, Dict, Any, Set, Tuple, Any
from difflib import SequenceMatcher
from app.services.g2p_service import convert_to_phonemes_with_mapping
from app.services.phonology_service import apply_phonological_variants
import string
from IPAkor.transcription import UniTranscript
t = UniTranscript()

def diff_by_type(
    correct_phs,
    user_phs,
    correct_types,
    user_types,
    correct_mapping,
    user_mapping,
    correct_chars,
    user_chars,
    allowed_variants,
    correct_original_phs,
    user_original_phs,
    correct_positions,
    user_positions,
    reference,
    user_text
):
    from collections import defaultdict
    from difflib import SequenceMatcher
    import string

    diff = []
    char_errors = {}
    error_analysis = []

    matcher = SequenceMatcher(None, correct_phs, user_phs)

    def find_near_same_jamo(pos_list, base_idx, jamo_idx):
        for delta in range(-2, 3):
            idx = base_idx + delta
            if 0 <= idx < len(pos_list) and pos_list[idx][1] == jamo_idx:
                return idx
        return None

    def safe_get(chars, mapping, idx):
        if idx is None:
            return ""
        if 0 <= idx < len(mapping):
            mapped = mapping[idx]
            if 0 <= mapped < len(chars):
                return chars[mapped]
        return ""

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        if tag == "replace" and (i2 - i1 > 1) and (j2 - j1 == 1):
            for k in range(i1, i2 - 1):
                cp = correct_phs[k]
                if cp == " ":
                    continue
                diff.append({"wrong": "", "correct": cp})
                mapped_idx = correct_mapping[k]
                if mapped_idx not in char_errors:
                    char_errors[mapped_idx] = {
                        "wrong": "",
                        "correct": reference[mapped_idx],
                        "index": mapped_idx
                    }
            i1 = i2 - 1
            j1 = j2 - 1
            tag = "replace"
            i2 = i1 + 1
            j2 = j1 + 1

        correct_span = correct_phs[i1:i2]
        user_span = user_phs[j1:j2]
        max_len = max(len(correct_span), len(user_span))

        for offset in range(max_len):
            correct_idx = i1 + offset if offset < len(correct_span) else None
            user_idx = j1 + offset if offset < len(user_span) else None

            cp = correct_phs[correct_idx] if correct_idx is not None else ""
            up = user_phs[user_idx] if user_idx is not None else ""

            if correct_idx is not None and user_idx is not None:
                if correct_positions[correct_idx][1] != user_positions[user_idx][1]:
                    new_user_idx = find_near_same_jamo(user_positions, user_idx, correct_positions[correct_idx][1])
                    if new_user_idx is not None:
                        user_idx = new_user_idx
                        up = user_phs[user_idx]

            if correct_idx is not None and user_idx is not None:
                if correct_idx < len(correct_original_phs) and user_idx < len(user_original_phs):
                    if correct_original_phs[correct_idx] == user_original_phs[user_idx]:
                        continue

            if cp and up:
                test = correct_phs[:]
                if correct_idx is not None:
                    test[correct_idx] = up
                if ''.join(test) in allowed_variants:
                    continue

            if correct_idx is not None and user_idx is not None:
                if correct_positions[correct_idx][1] != user_positions[user_idx][1]:
                    up = ""

            if (cp.strip() == "" and up.strip() == "") or (cp in string.punctuation):
                continue

            if correct_idx is not None and (user_idx is None or user_idx >= len(user_phs)):
                up = ""

            if (not cp.strip() and not up.strip()) or cp.isspace():
                continue

            diff.append({
                "wrong": up,
                "correct": cp
            })

            mapped_idx = correct_mapping[correct_idx] if correct_idx is not None and correct_idx < len(correct_mapping) else -1

            # default
            wrong_char = safe_get(user_text, user_mapping, user_idx)

            # 종성 누락일 경우 fallback
            if tag in ("delete", "replace") and correct_idx is not None:
                jamo_type = correct_types[correct_idx]
                mapped_idx = correct_mapping[correct_idx]
                correct_char = reference[mapped_idx] if 0 <= mapped_idx < len(correct_chars) else ""

                if jamo_type == 2 and up == "":
                    # 종성 누락 → 초/중 발음은 했으므로 같은 글자나 직전 글자에서 추정
                    wrong_char = user_text[mapped_idx] if 0 <= mapped_idx < len(user_text) else ""
                    if not wrong_char.strip() and mapped_idx - 1 >= 0:
                        wrong_char = user_text[mapped_idx - 1]

                if mapped_idx != -1 and mapped_idx not in char_errors:
                    char_errors[mapped_idx] = {
                        "wrong": wrong_char,
                        "correct": correct_char,
                        "index": mapped_idx
                    }

            # 오류 맥락 기록
            prev = correct_phs[correct_idx - 1] if correct_idx and correct_idx > 0 else ""
            next_ph = correct_phs[correct_idx + 1] if correct_idx is not None and correct_idx + 1 < len(correct_phs) else ""
            jamo_type = correct_types[correct_idx] if correct_idx is not None and correct_idx < len(correct_types) else -1

            user_char_idx = user_mapping[user_idx] if user_idx is not None and user_idx < len(user_mapping) else -1
            if jamo_type == 2 and up == "":
                user_char_idx -= 1

            if up == "":
                if jamo_type == 2:
                    tmp_idx = correct_mapping[correct_idx]
                    if tmp_idx < 0 or tmp_idx >= len(user_chars) or user_chars[tmp_idx].strip() == "":
                        error_index = -1
                    else:
                        error_index = tmp_idx
                else:
                    error_index = -1
            else:
                error_index = user_mapping[user_idx] if user_idx is not None else -1

            if not (up == "" and error_index == -1):
                if error_index in char_errors and char_errors[error_index]["wrong"] != "":
                    error_analysis.append({
                        "target": cp,
                        "user": up,
                        "jamoIndex": correct_positions[correct_idx][1],
                        "prev": prev,
                        "next": next_ph,
                        "errorIndex": error_index
                    })

    return {
        "diff": diff,
        "pronunciationErrors": list(char_errors.values()),
        "errorAnalysis": error_analysis
    }

def evaluate_pronunciation_with_index(reference: str, user_text: str) -> Dict[str, Any]:
    correct_phonemes, correct_mapping, correct_chars, correct_types, correct_original_phs, correct_positions = convert_to_phonemes_with_mapping(reference)
    user_phonemes, user_mapping, user_chars, user_types, user_original_phs, user_positions = convert_to_phonemes_with_mapping(user_text)

    allowed_variants = apply_phonological_variants(''.join(correct_phonemes))

    result = diff_by_type(
        correct_phs=correct_phonemes,
        user_phs=user_phonemes,
        correct_types=correct_types,
        user_types=user_types,
        correct_mapping=correct_mapping,
        user_mapping=user_mapping,
        correct_chars=correct_chars,
        user_chars=user_chars,
        allowed_variants=allowed_variants,
        correct_original_phs=correct_original_phs,
        user_original_phs=user_original_phs,
        correct_positions=correct_positions,
        user_positions=user_positions,
        reference = reference,
        user_text = user_text
    )

    filtered_user_phonemes = [
        ph for ph in user_phonemes
        if ph.strip() != "" and ph not in string.punctuation
    ]

    filtered_correct_phonemes = [
        ph for ph in correct_phonemes
        if ph.strip() != "" and ph not in string.punctuation
    ]

    passed = (
        len(result["pronunciationErrors"]) == 0 and
        len(filtered_user_phonemes) == len(filtered_correct_phonemes)
    )
    
    return {
        "reference": reference,
        "userText": user_text,
        "userIpa": t.transcribator(user_text),
        "errorDetails": {
            "correctPhonemes": correct_phonemes,
            "userPhonemes": user_phonemes,
            "diff": result["diff"]
        },
        "pronunciationErrors": result["pronunciationErrors"],
        "errorAnalysis": result["errorAnalysis"],
        "passed": passed
    }
