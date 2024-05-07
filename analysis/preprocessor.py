import collections

import nltk
import pymorphy2
import spacy
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize


class Preprocessor:
    def __init__(self, texts):
        self.texts = texts
        self.tokenized_texts = []
        self.texts_without_functional_pos = []
        self._lemmatized_texts = []
        self._texts_stemming = []

    def tokenize(self):
        for text in self.texts:
            self.tokenized_texts.append(word_tokenize(text))

    def remove_functional_pos(self):
        morph = pymorphy2.MorphAnalyzer()
        tokens = []

        for text in self.tokenized_texts:
            for token in text:
                if morph.parse(token) and morph.parse(token)[0].tag.POS not in ("PREP", "CONJ", "PRCL"):
                    tokens.append(token)
            self.texts_without_functional_pos.append(" ".join(tokens))

        return self.texts_without_functional_pos

    def lemmatize(self):
        nlp = spacy.load('en_core_web_sm', disable = ['parser', 'ner'])
        lemmatized_texts = []
        for text in self.texts:
            doc = nlp(text.lower())
            lemmatized_text = [token.lemma_ for token in doc]
            self._lemmatized_texts.append(lemmatized_text)

    def stemming(self):
        stemmer = SnowballStemmer(language='russian')
        for tokenized_text in self.tokenized_texts:
            self._texts_stemming.append(list(map(stemmer.stem, tokenized_text)))

    def get_unique_words(self):
        unique_words_in_text = []
        unique_words = []
        for text in self._lemmatized_texts:
            for word, number in collections.Counter(text).items():
                if number == 1:
                    unique_words_in_text.append(word)
            unique_words.append(unique_words_in_text)
        return unique_words

    def get_stemming(self):
        return self._texts_stemming

    def get_lemmatizing(self):
        return self._lemmatized_texts


