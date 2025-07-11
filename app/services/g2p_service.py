
# app/services/g2p_service.py

from g2pk import G2p
from typing import List, Tuple
from jamo import h2j, hangul_to_jamo
import hgtk

# G2P 객체 초기화 (전역)
g2p = G2p()

def convert_to_phonemes(text: str) -> List[str]:
    """
    한글 텍스트를 G2PK를 이용해 음소 리스트로 변환
    예: "좋아해" → ['ㅈ', 'ㅗ', 'ㅎ', 'ㅏ', 'ㅎ', 'ㅐ']
    """
    g2p_result = g2p(text)         # 예: "조아해"
    return list(hangul_to_jamo(g2p_result))  # 예: ['ㅈ', 'ㅗ', 'ㅇ', 'ㅏ', 'ㅎ', 'ㅐ']

def convert_to_phonemes_with_mapping(text: str) -> Tuple[
    List[str], List[int], List[str], List[int], List[str], List[Tuple[int, int]]
]:
    g2p_text = g2p(text)
    phonemes = []
    mapping = []
    phoneme_types = []  # 0: 초성, 1: 중성, 2: 종성
    chars = list(g2p_text)
    original_chars = list(text)
    original_phonemes = list(hangul_to_jamo(text))

    jamo_positions = []  # 추가: (음절 index, jamo index)

    for i, char in enumerate(chars):
        if hgtk.checker.is_hangul(char):
            try:
                cho, jung, jong = hgtk.letter.decompose(char)
                parts = [(cho, 0), (jung, 1)]
                if jong:
                    parts.append((jong, 2))

                for j, (phoneme, p_type) in enumerate(parts):
                    phonemes.append(phoneme)
                    mapping.append(i)
                    phoneme_types.append(p_type)
                    jamo_positions.append((i, p_type))  # i: 음절 index, p_type: jamo 위치

            except hgtk.exception.NotHangulException:
                phonemes.append(char)
                mapping.append(i)
                phoneme_types.append(-1)
                jamo_positions.append((i, -1))
        else:
            phonemes.append(char)
            mapping.append(i)
            phoneme_types.append(-1)
            jamo_positions.append((i, -1))

    return phonemes, mapping, chars, phoneme_types, original_phonemes, jamo_positions