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

def convert_to_phonemes_with_mapping(text: str) -> Tuple[List[str], List[int], List[str]]:
    """
    G2P 변환 + 정확한 음소-글자 매핑
    """
    g2p_text = g2p(text)  # 예: "좋아해" -> "조아해"
    phonemes = []
    mapping = []
    chars = list(g2p_text)

    for i, char in enumerate(chars):
        if hgtk.checker.is_hangul(char):
            try:
                cho, jung, jong = hgtk.letter.decompose(char)
                parts = [cho, jung] + ([jong] if jong else [])
                phonemes.extend(parts)
                mapping.extend([i] * len(parts))
            except hgtk.exception.NotHangulException:
                phonemes.append(char)
                mapping.append(i)
        else:
            phonemes.append(char)
            mapping.append(i)

    return phonemes, mapping, chars