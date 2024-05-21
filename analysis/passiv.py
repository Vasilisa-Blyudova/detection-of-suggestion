import pandas as pd
import pymorphy2
import spacy
import stanza
from deeppavlov import build_model
from natasha import (Doc, NewsEmbedding, NewsMorphTagger, NewsNERTagger,
                     Segmenter)
from config.constants import ASSETS_PATH, DATA_PATH


def load_data(path, format="csv"):
    if format == 'csv':
        data = pd.read_csv(path)
    else:
        data = pd.read_excel(path, engine="openpyxl")
    return data


def analyzes_pymorphy(tag: set, text):
    morph = pymorphy2.MorphAnalyzer()
    tokens = []

    for token in text.split():
        if morph.parse(token) and tag in morph.parse(token)[0].tag:
            tokens.append(token)

    return tokens


def analyzes_spacy(pos, tag_name, tag_value, text):
    nlp = spacy.load("ru_core_news_sm")
    doc = nlp(text)

    tokens = []

    for token in doc:
        if token.pos_ == pos and \
                token.morph.to_dict().get(tag_name) == tag_value:
            tokens.append(token)

    return tokens


def analyzes_stanza(pos, tag, text):
    nlp = stanza.Pipeline('ru', verbose=False)
    doc = nlp(text)
    if tag:
        tokens = [word.text for sentence in doc.sentences for token in sentence.tokens
                  for word in token.words if word.upos == pos and tag in word.feats]
    else:
        tokens = [word.text for sentence in doc.sentences for token in sentence.tokens
                  for word in token.words if word.upos == pos]

    return tokens


def analyzes_natasha(pos, tag_name, tag_value, text):
    segmenter = Segmenter()

    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)

    tokens = []

    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for sentence in doc.sents:
        for token in sentence.morph.tokens:
            if token.pos == pos and token.feats.get(tag_name) == tag_value:
                tokens.append(token.text)

    return tokens


def main():
    dataset = load_data(DATA_PATH)

    for id, text in enumerate(dataset['wb_descriptions']):
        print(f"{id}-----------------------------------------------------------------")
        print(analyzes_pymorphy({"VERB", "pssv"}, text))
        print(analyzes_spacy("VERB", "Voice", "Pass", text))
        print(analyzes_stanza("VERB", "Voice=Pass", text))
        print(analyzes_natasha("VERB", "Voice", "Pass", text))


if __name__ == "__main__":
    main()
