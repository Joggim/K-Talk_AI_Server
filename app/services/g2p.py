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
    띄어쓰기 단위로 G2P 변환 후 음소 분해 및 음소-글자 매핑
    Returns:
        - phonemes: 전체 음소 리스트
        - phoneme_to_char_index: 각 음소가 어떤 글자에서 나왔는지 매핑한 인덱스
        - all_chars: G2P 변환된 전체 글자 리스트
    """
    words = text.strip().split()
    phonemes = []
    mapping = []
    all_chars = []

    char_index_offset = 0  # 전체 글자 기준 인덱스를 유지

    for word in words:
        g2p_text = g2p(word)  # 예: "좋아해요" -> "조아해요"
        chars = list(g2p_text)
        all_chars.extend(chars)

        for i, char in enumerate(chars):
            if hgtk.checker.is_hangul(char):
                try:
                    cho, jung, jong = hgtk.letter.decompose(char)
                    parts = [cho, jung] + ([jong] if jong else [])
                    phonemes.extend(parts)
                    mapping.extend([char_index_offset + i] * len(parts))
                except hgtk.exception.NotHangulException:
                    phonemes.append(char)
                    mapping.append(char_index_offset + i)
            else:
                phonemes.append(char)
                mapping.append(char_index_offset + i)

        char_index_offset += len(chars)

    return phonemes, mapping, all_chars