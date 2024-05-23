import pymorphy2


def analyzes_pymorphy(tag: set, text):
    morph = pymorphy2.MorphAnalyzer()
    tokens = []

    for token in text.split():
        if morph.parse(token) and tag in morph.parse(token)[0].tag:
            tokens.append(token)

    return tokens
