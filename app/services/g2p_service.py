# app/services/g2p_service.py

from g2pk import G2p
from typing import List
from jamo import h2j, hangul_to_jamo

# G2P 객체 초기화 (전역)
g2p = G2p()

def convert_to_phonemes(text: str) -> List[str]:
    """
    한글 텍스트를 G2PK를 이용해 음소 리스트로 변환
    예: "좋아해" → ['ㅈ', 'ㅗ', 'ㅎ', 'ㅏ', 'ㅎ', 'ㅐ']
    """
    g2p_result = g2p(text)         # 예: "조아해"
    return list(hangul_to_jamo(g2p_result))  # 예: ['ㅈ', 'ㅗ', 'ㅇ', 'ㅏ', 'ㅎ', 'ㅐ']
