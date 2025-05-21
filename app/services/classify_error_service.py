def classify_error_rule_final(target, user, prev, next_, pos):

    diphthongs = {'ㅘ', 'ㅙ', 'ㅚ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅢ'}
    vowels = {'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ',
              'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ',
              'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ'}
    consonants = set('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')

    # 기본값
    error_type = "미분류"

    if target in ['ㄲ', 'ㄸ', 'ㅃ', 'ㅉ'] and user in ['ㄱ', 'ㄷ', 'ㅂ', 'ㅈ'] and pos == 0:
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
        if target in diphthongs:
            error_type = "이중모음오류"
        else:
            error_type = "모음혼동"

    elif pos == 2 and target != user:

        if target == "":

            error_type = "받침추가"

        elif user == "":

            error_type = "받침탈락"

        elif target in consonants and user in consonants:

            error_type = "받침대치"

        elif pos != 2 and target in consonants and user in consonants and target != user:

            error_type = "자음혼동"

    return f"{error_type}" if error_type != "미분류" else "미분류"
