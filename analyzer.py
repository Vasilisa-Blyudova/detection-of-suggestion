import pandas as pd
import pymorphy2
import spacy
import stanza
from deeppavlov import build_model
from natasha import (Doc, NewsEmbedding, NewsMorphTagger, NewsNERTagger,
                     Segmenter)


def read_from_csv(file_name: str):
    return pd.read_csv(file_name)


class FeatureAnalyzer:
    def __init__(self, tokenized_text):
        self.text = tokenized_text

    def analyzes_pymorphy(self, tag: set):
        morph = pymorphy2.MorphAnalyzer()
        tokens = []

        for token in self.text.split():
            if morph.parse(token) and tag in morph.parse(token)[0].tag:
                tokens.append(token)

        return tokens

    def analyzes_spacy(self, pos, tag_name: str = None, tag_value: str = None):
        nlp = spacy.load("ru_core_news_sm")
        doc = nlp(self.text)

        tokens = []

        for token in doc:
            if token.pos_ == pos and \
                    token.morph.to_dict().get(tag_name) == tag_value:
                tokens.append(token)

        return tokens

    def analyzes_stanza(self, pos, tag: str = None):
        nlp = stanza.Pipeline('ru', verbose=False)
        doc = nlp(self.text)
        if tag:
            tokens = [word.text for sentence in doc.sentences for token in sentence.tokens
                      for word in token.words if word.upos == pos and tag in word.feats]
        else:
            tokens = [word.text for sentence in doc.sentences for token in sentence.tokens
                      for word in token.words if word.upos == pos]

        return tokens

    def analyzes_natasha(self, pos, tag_name: str = None, tag_value: str = None):
        segmenter = Segmenter()

        emb = NewsEmbedding()
        morph_tagger = NewsMorphTagger(emb)

        tokens = []

        doc = Doc(self.text)
        doc.segment(segmenter)
        doc.tag_morph(morph_tagger)
        for sentence in doc.sents:
            for token in sentence.morph.tokens:
                if token.pos == pos and token.feats.get(tag_name) == tag_value:
                    tokens.append(token.text)

        return tokens

    def analyzes_stanza_ner(self):
        nlp = stanza.Pipeline(lang='ru', processors='tokenize,ner')
        doc = nlp(self.text)

        tokens = []

        for token in doc.ents:
            tokens.append(token.text)

        return tokens

    def analyzes_natasha_ner(self):
        segmenter = Segmenter()

        emb = NewsEmbedding()
        ner_tagger = NewsNERTagger(emb)

        tokens = []

        doc = Doc(self.text)
        doc.segment(segmenter)
        doc.tag_ner(ner_tagger)
        for ent in doc.spans:
            tokens.append(ent.text)

        return tokens

    def analyzes_deeppavlov_ner(self):
        text = [self.text]
        ner_model = build_model('ner_rus_bert', download=True, install=True)

        tokens = []
        for words, labels in zip(ner_model(text)[0], ner_model(text)[1]):
            for token, label in zip(words, labels):
                if label != "O":
                    tokens.append(token)

        return tokens


def get_numerals(analyzer: FeatureAnalyzer):
    return analyzer.analyzes_pymorphy({"NUMR"}), \
           analyzer.analyzes_spacy(pos="NUM"), \
           analyzer.analyzes_stanza(pos="NUM"), \
           analyzer.analyzes_natasha(pos="NUM")


def get_imperative(analyzer: FeatureAnalyzer):
    return analyzer.analyzes_pymorphy({"VERB", "impr"}), \
           analyzer.analyzes_spacy(pos="VERB", tag_name="Mood", tag_value="Imp"), \
           analyzer.analyzes_stanza(pos="VERB", tag="Mood=Imp"), \
           analyzer.analyzes_natasha(pos="VERB", tag_name="Mood", tag_value="Imp")


def get_adjectives(analyzer: FeatureAnalyzer):
    return analyzer.analyzes_pymorphy({"ADJF", "Supr"}), \
           analyzer.analyzes_pymorphy({"ADJF", "Cmp2"}), \
           analyzer.analyzes_spacy(pos="ADJ", tag_name="Degree", tag_value="Cmp"), \
           analyzer.analyzes_spacy(pos="ADJ", tag_name="Degree", tag_value="Sup"), \
           analyzer.analyzes_stanza(pos="VERB", tag="Degree=Cmp"), \
           analyzer.analyzes_stanza(pos="VERB", tag="Degree=Sup"), \
           analyzer.analyzes_natasha(pos="ADJ", tag_name="Degree", tag_value="Cmp"), \
           analyzer.analyzes_natasha(pos="ADJ", tag_name="Degree", tag_value="Sup")


def get_passiv(analyzer: FeatureAnalyzer):
    return analyzer.analyzes_pymorphy({"VERB", "pssv"}), \
           analyzer.analyzes_spacy(pos="VERB", tag_name="Voice", tag_value="Pass"), \
           analyzer.analyzes_stanza(pos="VERB", tag="Voice=Pass"), \
           analyzer.analyzes_natasha(pos="VERB", tag_name="Voice", tag_value="Pass")


if __name__ == "__main__":
    data = read_from_csv("data.csv")

    for text in data["wb_descriptions"][:1]:
        analyzer = FeatureAnalyzer(text)

        print(analyzer.analyzes_deeppavlov_ner())

        print(analyzer.analyzes_stanza_ner())
        print(analyzer.analyzes_natasha_ner())

        print(get_numerals(analyzer))
        print(get_imperative(analyzer))
        print(get_adjectives(analyzer))
        print(get_passiv(analyzer))
