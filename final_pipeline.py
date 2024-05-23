import random
from typing import List


def generate_random_color() -> str:
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


def highlight_words(text: str, words_to_highlight: List[str]) -> str:
    for word in words_to_highlight:
        color = generate_random_color()
        text = text.replace(word, f'<span style="background-color:{color}">{word}</span>')
    return text


def process_text(text: str) -> str:
    words_to_highlight = ["слово1", "слово2", "слово3"]
    return highlight_words(text, words_to_highlight)
