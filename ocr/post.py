# 英文标点到中文标点的映射字典
punctuation_map = {
    ',': '，',
    '.': '。',
    ':': '：',
    ';': '；',
    '!': '！',
    '?': '？',
    '(': '（',
    ')': '）',
    '[': '【',
    ']': '】',
    '<': '《',
    '>': '》',
    '"': '“',
    "'": '‘',
    '`': '·'
}

# 中文标点集合
chinese_punctuation = set(punctuation_map.values())


# 英文符号转换与多余空格去除
def convert_punctuation_to_chinese(text):
    result = []
    i = 0
    n = len(text)

    while i < n:
        char = text[i]
        # 检查当前字符是否是英文标点
        if char in punctuation_map:
            # 替换为中文标点
            result.append(punctuation_map[char])
            # 检查下一个字符是否是空格，如果是则跳过
            if i + 1 < n and text[i + 1] == ' ':
                i += 1
        else:
            # 检查当前字符是否是中文标点
            if char in chinese_punctuation:
                result.append(char)
                # 检查下一个字符是否是空格，如果是则跳过
                if i + 1 < n and text[i + 1] == ' ':
                    i += 1
            else:
                result.append(char)
        i += 1

    return ''.join(result)
