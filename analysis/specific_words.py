from pathlib import Path

import nltk
import pandas as pd
import pymorphy2
import spacy
from nltk.tokenize import word_tokenize

from analysis.preprocessor import Preprocessor
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

def detect_specific_meaning(dictionary, text):
        common_words = []
        for word in text:
#             print(word)
            if not dictionary.loc[(dictionary["слово"] == word) & (dictionary["рейтинг"] < 3), "рейтинг"].empty:
                common_words.append(word)
        return common_words
#         if not common_words:
#             result.append(0)
#         print(common_words)
#         self._result.append(1)
#         print(f"OK! {self._result}")

def main():
    dataset = load_data(DATA_PATH)
    specific_words_dictionary = load_data(ASSETS_PATH / "specific_words_dictionary.xlsx", "xlsx")

    preprocessor = Preprocessor(dataset['wb_descriptions'])
    preprocessor.lemmatize()
    lemmatized_texts = preprocessor.get_lemmatized_texts()

    for text in lemmatized_texts[:5]:
        print(detect_specific_meaning(specific_words_dictionary, text))

if __name__ == "__main__":
    main()
