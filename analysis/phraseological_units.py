import math
from pathlib import Path

import pandas as pd
import pymorphy2
import spacy
import stanza
from natasha import (Doc, NewsEmbedding, NewsMorphTagger, NewsNERTagger,
                     Segmenter)

from config.constants import ASSETS_PATH, DATA_PATH


class Preprocessor:
    def __init__(self, texts):
        self.texts = texts
        self.tokenized_texts = []
        self._lemmatized_texts = []

    def tokenize(self):
        for text in self.texts:
            self.tokenized_texts.append(word_tokenize(text))

    def lemmatize(self):
        nlp = spacy.load('ru_core_news_lg', disable = ['parser', 'ner'])
        lemmatized_texts = []
        for text in self.texts:
            doc = nlp(text.lower())
            lemmatized_text = [token.lemma_ for token in doc]
            self._lemmatized_texts.append(lemmatized_text)

    def get_lemmatized_texts(self):
        return self._lemmatized_texts

def load_data(path, format="csv"):
    if format == 'csv':
        data = pd.read_csv(path)
    else:
        data = pd.read_excel(path, engine="openpyxl")
    return data

def detect_phraseological_units(phraseological_units_dictionary, text):
    common_unit = []
    for phraseological_unit in phraseological_units_dictionary["phraseological_units"].values:
        if phraseological_unit in ' '.join(text):
            common_unit.append(phraseological_unit)
    return common_unit

def main():
    dataset = load_data(DATA_PATH)
    phraseological_units_dictionary = load_data(ASSETS_PATH / "phraseological_units_dictionary.csv")

    preprocessor = Preprocessor(dataset['wb_descriptions'])
    preprocessor.lemmatize()
    lemmatized_texts = preprocessor.get_lemmatized_texts()

    for text in lemmatized_texts[:5]:
        print(detect_phraseological_units(phraseological_units_dictionary, text))

if __name__ == "__main__":
    main()