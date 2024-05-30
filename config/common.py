import pandas as pd
import pymorphy2
import spacy
import stanza
from natasha import Doc, NewsEmbedding, NewsMorphTagger, Segmenter


def load_data(path, file_format="csv"):
    if file_format == 'csv':
        data = pd.read_csv(path)
    else:
        # data = pd.read_excel(path)

        # df.to_csv(f"path_file\{datetime.now().strftime('%d-%m-%Y')}.xlsx", index=False, sep=';')
        data = pd.read_excel(path, engine="openpyxl")
    return data


def analyzes_pymorphy(text, pos: list | str = None, tag: str = None):
    morph = pymorphy2.MorphAnalyzer()
    tokens = []

    for token in text.split():
        if morph.parse(token):
            if isinstance(pos, list):
                for part_of_speech in pos:
                    if part_of_speech in morph.parse(token)[0].tag:
                        tokens.append(token)
            elif isinstance(pos, str):
                if pos in morph.parse(token)[0].tag and tag in morph.parse(token)[0].tag:
                    tokens.append(token)
            else:
                if tag in morph.parse(token)[0].tag:
                    tokens.append(token)

    return tokens


def analyzes_spacy(text: str, pos: str = None, tag_name: str = None, tag_value: str = None):
    nlp = spacy.load("ru_core_news_lg")
    doc = nlp(text)

    tokens = []

    for token in doc:
        if isinstance(pos, str):
            if token.pos_ == pos and \
                    token.morph.to_dict().get(tag_name) == tag_value:
                tokens.append(token.text)
        else:
            if token.morph.to_dict().get(tag_name) == tag_value:
                tokens.append(token.text)

    return tokens


def analyzes_stanza(text, pos: str = None, tag: str = None):
    nlp = stanza.Pipeline('ru', verbose=False)
    doc = nlp(text)
    if tag and not pos:
        tokens = [word.text for sentence in doc.sentences for token in sentence.tokens
                  for word in token.words if word.feats and tag in word.feats]
    elif tag and pos:
        tokens = [word.text for sentence in doc.sentences for token in sentence.tokens
                  for word in token.words if word.upos == pos and tag in word.feats]
    else:
        tokens = [word.text for sentence in doc.sentences for token in sentence.tokens
                  for word in token.words if word.upos == pos]

    return tokens


def analyzes_natasha(text, pos: str = None, tag_name: str = None, tag_value: str = None):
    segmenter = Segmenter()

    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)

    tokens = []

    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for sentence in doc.sents:
        for token in sentence.morph.tokens:
            if pos:
                if token.pos == pos and token.feats.get(tag_name) == tag_value:
                    tokens.append(token.text)
            else:
                if token.feats.get(tag_name) == tag_value:
                    tokens.append(token.text)

    return tokens
