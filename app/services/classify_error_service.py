def classify_error_rule_final(target, user, prev, next_, pos):

    vowels = {'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ',
              'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ',
              'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ'}
    consonants = set('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')

    # 기본값
    error_type = "미분류"

    if target in ['ㄱ', 'ㄷ', 'ㅂ', 'ㅈ'] and user in ['ㄲ', 'ㄸ', 'ㅃ', 'ㅉ'] and pos == 0:
        error_type = "된소리되기"

    elif {target, user} == {'ㄴ', 'ㄹ'} and ('ㄹ' in [prev, next_]):
        error_type = "유음화"

    elif target in ['ㄱ', 'ㄷ', 'ㅂ'] and pos == 2 and next_ in ['ㄴ', 'ㅁ']:
        error_type = "비음화"

    elif target in ['ㄷ', 'ㅌ'] and pos == 0 and next_ in ['ㅣ', 'ㅕ'] and target != user:
        error_type = "구개음화"

    elif pos == 0 and prev in ['ㄱ', 'ㅂ', 'ㄴ', 'ㄹ'] and target in ['ㄱ', 'ㅂ', 'ㅅ', 'ㅈ'] and target != user:
        error_type = "경음화"

    elif pos == 2 and target != user and next_ in ['ㅇ', 'ㅎ']:
        error_type = "연음화"

    elif pos == 2 and target in ['ㅅ', 'ㅆ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'] and target != user:
        error_type = "음절끝소리규칙"

    elif target in vowels and user in vowels and target != user:
        error_type = "모음혼동"


    elif pos == 2 and target in consonants and (user != target):
        # 종성 위치 + 자음이어야 할 자리인데, 공백이거나 잘못 발음한 경우
        error_type = "받침오류"

    elif target in consonants and user in consonants and target != user:
        # 종성이 아닌 자리에 자음 혼동
        error_type = "자음혼동"

    return f"{error_type}" if error_type != "미분류" else "미분류"
