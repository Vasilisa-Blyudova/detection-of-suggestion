from typing import List

from pipeline import analyzes_pymorphy


def highlight_words(text: str, words_to_highlight: List[str], color) -> str:
    for word in words_to_highlight:
        # color = generate_random_color()
        text = text.replace(word, f'<span style="background-color:{color}">{word}</span>')
    return text


def process_text(text: str) -> str:
    words_to_highlight = analyzes_pymorphy({"VERB", "impr"}, text)
    return highlight_words(text, words_to_highlight, "#ffb3ba")
