from typing import List, Dict, Any, Set
from difflib import SequenceMatcher
from app.services.g2p_service import convert_to_phonemes_with_mapping
from app.services.phonology_service import apply_phonological_variants

def is_ignorable_phoneme(ph: str) -> bool:
    return ph in {"", " ", "\n"}

def diff_by_type(
    correct_phs,
    user_phs,
    correct_types,
    user_types,
    correct_mapping,
    user_mapping,
    correct_chars,
    user_chars,
    allowed_variants
):
    diff = []
    char_errors = {}
    error_analysis = []

    matcher = SequenceMatcher(None, correct_phs, user_phs)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        for offset in range(max(i2 - i1, j2 - j1)):
            correct_idx = i1 + offset if i1 + offset < len(correct_phs) else None
            user_idx = j1 + offset if j1 + offset < len(user_phs) else None
            
            cp = correct_phs[correct_idx] if tag != "insert" else ""
            up = user_phs[user_idx] if tag != "delete" else ""
            
            # 허용된 변형이면 무시
            if cp and up:
                test = correct_phs[:]
                test[correct_idx] = up
                if ''.join(test) in allowed_variants:
                    continue
            
            # 공백이면 무시
            if cp == "" and up == " " or cp == " " and up == "":
                continue
            
            # diff 저장
            diff.append({
                "wrong": up,
                "correct": cp
            })

            # 글자 오류 기록
            if tag == "insert" and user_idx is not None:
                # wrong 인덱스는 그대로
                wrong_mapping_idx = user_mapping[user_idx]

                # correct 인덱스는 종성일 경우 -1 보정
                if correct_idx is not None and user_types[user_idx] == 2 and correct_idx > 0:
                    correct_mapping_idx = correct_mapping[correct_idx - 1]
                elif correct_idx is not None:
                    correct_mapping_idx = correct_mapping[correct_idx]
                else:
                    correct_mapping_idx = -1

                wrong_char = user_chars[wrong_mapping_idx] if wrong_mapping_idx < len(user_chars) else ""
                correct_char = correct_chars[correct_mapping_idx] if correct_mapping_idx != -1 and correct_mapping_idx < len(correct_chars) else ""
                mapped_idx = correct_mapping_idx

            elif tag == "delete" and correct_idx is not None:
                # correct 인덱스는 그대로
                correct_mapping_idx = correct_mapping[correct_idx]

                # wrong 인덱스는 종성일 경우 -1 보정
                if user_idx is not None and correct_types[correct_idx] == 2 and user_idx > 0:
                    wrong_mapping_idx = user_mapping[user_idx - 1]
                elif user_idx is not None:
                    wrong_mapping_idx = user_mapping[user_idx]
                else:
                    wrong_mapping_idx = -1

                wrong_char = user_chars[wrong_mapping_idx] if wrong_mapping_idx != -1 and wrong_mapping_idx < len(user_chars) else ""
                correct_char = correct_chars[correct_mapping_idx] if correct_mapping_idx < len(correct_chars) else ""
                mapped_idx = correct_mapping_idx
                
            elif tag == "replace" and user_idx is not None and correct_idx is not None:
                mapped_idx = correct_mapping[correct_idx]
                if correct_types[correct_idx] == 2 and user_phs[user_idx] == " " and user_idx > 0:
                    wrong_mapping_idx = user_mapping[user_idx - 1]
                else:
                    wrong_mapping_idx = user_mapping[user_idx]

                wrong_char = user_chars[wrong_mapping_idx] if wrong_mapping_idx < len(user_chars) else ""
                correct_char = correct_chars[mapped_idx] if mapped_idx < len(correct_chars) else ""
                
            else:
                mapped_idx = -1
                wrong_char = ""
                correct_char = ""

            if mapped_idx != -1 and mapped_idx not in char_errors:
                char_errors[mapped_idx] = {
                    "wrong": wrong_char,
                    "correct": correct_char,
                    "index": mapped_idx
                }

            # 오류 맥락 분석
            prev = correct_phs[correct_idx - 1] if correct_idx and correct_idx > 0 else ""
            next_ph = correct_phs[correct_idx + 1] if correct_idx is not None and correct_idx + 1 < len(correct_phs) else ""
            jamo_type = correct_types[correct_idx] if correct_idx is not None and correct_idx < len(correct_types) else -1

            error_analysis.append({
                "target": cp,
                "user": up,
                "jamo_index_in_syllable": jamo_type,
                "prev": prev,
                "next": next_ph
            })

    return {
        "diff": diff,
        "pronunciationErrors": list(char_errors.values()),
        "errorAnalysis": error_analysis
    }
    
def evaluate_pronunciation_with_index(reference: str, user_text: str) -> Dict[str, Any]:
    correct_phonemes, correct_mapping, correct_chars, correct_types = convert_to_phonemes_with_mapping(reference)
    user_phonemes, user_mapping, user_chars, user_types = convert_to_phonemes_with_mapping(user_text)

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
        allowed_variants=allowed_variants
    )

    return {
        "reference": reference,
        "userText": user_text,
        "errorDetails": {
            "correctPhonemes": correct_phonemes,
            "userPhonemes": user_phonemes,
            "diff": result["diff"]
        },
        "pronunciationErrors": result["pronunciationErrors"],
        "errorAnalysis": result["errorAnalysis"],
        "passed": len(result["pronunciationErrors"]) == 0
    }
