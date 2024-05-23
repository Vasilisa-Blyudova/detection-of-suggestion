import pymorphy2
import spacy
import stanza
from natasha import Doc, NewsEmbedding, NewsMorphTagger, Segmenter

from config.common import load_data
from config.constants import DATA_PATH


def analyzes_pymorphy(tag: set, text):
    morph = pymorphy2.MorphAnalyzer()
    tokens = []

    for token in text.split():
        print(morph.parse(token))
        if morph.parse(token) and tag in morph.parse(token)[0].tag:
            tokens.append(token)

    return tokens


def analyzes_spacy(pos, tag_name, tag_value, text):
    nlp = spacy.load("ru_core_news_lg")
    doc = nlp(text)

    tokens = []

    for token in doc:
        print(token.morph)
        print(token.pos_)
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
        print(sentence.morph.tokens)
        for token in sentence.morph.tokens:
            if token.pos == pos and token.feats.get(tag_name) == tag_value:
                tokens.append(token.text)

    return tokens


def main():
    dataset = load_data(DATA_PATH)

    for id, text in enumerate(dataset['wb_descriptions'][:1]):
        print(f"{id}----------------------------------------------")
        print("Превосходная степень прилагательных")
        print("result: ", analyzes_pymorphy({"ADJF", "Supr"}, text))
        print("result: ", analyzes_spacy(pos="ADJ", tag_name="Degree", tag_value="Sup", text=text))
        print("result: ", analyzes_stanza(pos="ADJ", tag="Degree=Sup", text=text))
        print("result: ", analyzes_natasha(pos="ADJ", tag_name="Degree", tag_value="Sup", text=text))
        print("Сравнительная степень прилагательных")
        print("result: ", analyzes_pymorphy({"ADJF", "Cmp2"}, text))
        print("result: ", analyzes_spacy(pos="ADJ", tag_name="Degree", tag_value="Cmp", text=text))
        print("result: ", analyzes_stanza(pos="ADJ", tag="Degree=Cmp", text=text))
        print("result: ", analyzes_natasha(pos="ADJ", tag_name="Degree", tag_value="Cmp", text=text))


if __name__ == "__main__":
    main()
