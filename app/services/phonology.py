from typing import Set
import itertools

# 표준 발음법에 근거하여 g2pk가 커버하지 않는 주요 규칙만 추가
PHONOLOGICAL_RULES = [
    # 연음화: 받침 + 'ㅇ' 초성 → 받침이 옮겨감
    ('ㄴㅇ', 'ㄴㄴ'),  # 예: 신여자 → 신녀자
    ('ㄹㅇ', 'ㄹㄹ'),  # 설이 → 서리

    # 비음화
    ('ㄱㄴ', 'ㅇㄴ'),  # 국물 → 궁물
    ('ㄱㅁ', 'ㅇㅁ'),
    ('ㅂㄴ', 'ㅁㄴ'),
    ('ㅂㅁ', 'ㅁㅁ'),
    ('ㄷㄴ', 'ㄴㄴ'),

    # 유음화
    ('ㄴㄹ', 'ㄹㄹ'),  # 신라 → 실라
    ('ㄹㄴ', 'ㄹㄹ'),  # 설날 → 설랄

    # 경음화
    ('ㄱㄱ', 'ㄲ'), 
    ('ㄷㄷ', 'ㄸ'), 
    ('ㅂㅂ', 'ㅃ'), 
    ('ㅈㅈ', 'ㅉ'), 
    ('ㄱㅎ', 'ㅋ'),
    ('ㄷㅎ', 'ㅌ'),
    ('ㅂㅎ', 'ㅍ'),
    ('ㅈㅎ', 'ㅊ'),
]

# 허용 발음 조합 생성 함수
def apply_phonological_variants(phoneme: str) -> Set[str]:
    variants = set([phoneme])
    positions = []
    
     # 적용 가능한 위치 추적
    for pattern, replacement in PHONOLOGICAL_RULES:
        start = 0
        while True:
            idx = phoneme.find(pattern, start)
            if idx == -1:
                break
            positions.append((idx, pattern, replacement))
            start = idx + 1
    
    # 가능한 모든 규칙 조합으로 대체
    for i in range(1, len(positions) + 1):
        for combo in itertools.combinations(positions, i):
            temp = phoneme
            offset = 0
            for idx, pattern, replacement in combo:
                adjusted_idx = idx + offset
                if temp[adjusted_idx:adjusted_idx + len(pattern)] == pattern:
                    temp = temp[:adjusted_idx] + replacement + temp[adjusted_idx + len(pattern):]
                    offset += len(replacement) - len(pattern)
            variants.add(temp)
    return variants
