from analysis.antonyms import detect_antonyms
from analysis.lexical_repetitions import calculate_mattr_index
from analysis.loanwords import get_loanwords
from analysis.ner import analyzes_deeppavlov_ner
from analysis.phraseological_units import detect_phraseological_units
from analysis.preprocessor import Preprocessor
from analysis.specific_words import detect_specific_meaning
from config.common import analyzes_stanza, analyzes_spacy, analyzes_pymorphy
from config.constants import ASSETS_PATH
from config.service_settings import ServiceSettings


def highlight_words(text: str) -> str:
    analysis = get_analysis(text)
    colors = get_colors()
    for color, words in zip(colors, analysis):
        if isinstance(words, float):
            continue
        for word in words:
            text = text.replace(word, f'<span style="background-color:{color}">{word}</span>')
    return text


def get_analysis(text: str) -> list:
    preprocessor = Preprocessor([text])
    preprocessor.lemmatize()
    lemmatized_text = preprocessor.get_lemmatizing()
    return [analyzes_deeppavlov_ner(text),
            detect_specific_meaning(lemmatized_text[0]),
            get_loanwords(text),
            calculate_mattr_index(text),
            detect_antonyms(lemmatized_text[0]),
            analyzes_stanza(text, "NUM"),
            detect_phraseological_units(lemmatized_text[0]),
            analyzes_spacy(text, "VERB", "Mood", "Imp"),
            analyzes_pymorphy(text, "ADJF", "Supr") + analyzes_pymorphy(text, "ADJF", "Cmp2"),
            analyzes_stanza(text, tag="Voice=Pass")]


def get_weights() -> dict:
    settings = ServiceSettings(ASSETS_PATH / 'settings.json')
    return settings.weights


def get_colors() -> list:
    settings = ServiceSettings(ASSETS_PATH / 'settings.json')
    return settings.colors


def get_threshold() -> float:
    settings = ServiceSettings(ASSETS_PATH / 'settings.json')
    return settings.threshold


def get_icons_list(text):
    result = []
    analysis = get_analysis(text)
    for feature_analysis in analysis:
        if isinstance(feature_analysis, float):
            if feature_analysis > 0.7:
                result.append(0)
            else:
                result.append(1)
        elif isinstance(feature_analysis, list):
            if feature_analysis:
                result.append(1)
            else:
                result.append(0)
    return result


def get_score(text):
    final_score = 0
    results = get_icons_list(text)
    weights = list(get_weights().values())
    for result, weight in zip(results, weights):
        final_score += result * weight

    return round(final_score, 2)


def get_result(final_score):
    threshold = get_threshold()

    if final_score >= threshold:
        return "текст суггестивный"
    else:
        return "текст несуггестивный"
