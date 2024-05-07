import json
import os
from pathlib import Path

import pandas as pd
import pymorphy2
import spacy
import stanza
import torch
from deeppavlov import build_model, configs
from natasha import (Doc, NewsEmbedding, NewsMorphTagger, NewsNERTagger,
                     Segmenter)
from sparknlp.pretrained import PretrainedPipeline
from torch.utils.data import DataLoader, Dataset
from transformers import (AutoModelForTokenClassification, AutoTokenizer,
                          TFXLMRobertaForTokenClassification,
                          XLMRobertaForTokenClassification)

from config.constants import ASSETS_PATH, DATA_PATH

# import tensorflow as tf


# os.environ["STANZA_RESOURCES_DIR"] = "D:/stanza_resources"
# stanza.download("ru")

os.environ["DEEPPAVLOV_MODELS_PATH"] = "D:\deeppavlov"

def load_data(path, format="csv"):
    if format == 'csv':
        data = pd.read_csv(path)
    else:
        data = pd.read_excel(path, engine="openpyxl")
    return data

# xlm-roberta reference

class CustomDataset(Dataset):

    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index: int) -> tuple[str, ...]:
        return (str(self.data["wb_descriptions"].iloc[index]),)

class LLMPipeline:
    def __init__(self, model_name: str, dataset: CustomDataset,
                 batch_size: int, device: str) -> None:
        super(LLMPipeline, self).__init__()

        self._dataset = dataset

        self._model = XLMRobertaForTokenClassification.from_pretrained(model_name)
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)

        self._batch_size = batch_size

    def infer_sample(self, sample: tuple[str, ...]):
        res = self._infer_batch(sample)
        return res

    def infer_dataset(self) -> pd.DataFrame:
        predictions = []
        dataset_loader = DataLoader(self._dataset, batch_size=self._batch_size)

        for batch_data in dataset_loader:
            predictions.append(self._infer_batch(batch_data))
        predictions_df = pd.DataFrame({"predictions": predictions})

        return predictions_df

    def _infer_batch(self, sample_batch) -> list[str]:
        inputs = self._tokenizer(
            sample_batch[0],
            add_special_tokens=False,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )
        tokens = self._tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
#         print(tokens)

        logits = self._model(**inputs).logits
        predictions = torch.argmax(logits, dim=2)

        predicted_tokens_classes = [self._model.config.id2label[t.item()] for t in predictions[0]]
        return predicted_tokens_classes

# Stanza

def analyzes_stanza_ner(text):
    nlp = stanza.Pipeline(lang='ru', processors='tokenize,ner')
    doc = nlp(text)

    tokens = []

    for token in doc.ents:
        tokens.append(token.text)

    return tokens

# Deep Pavlov

def analyzes_deeppavlov_ner(text):
    text = [text]
#     with configs.ner.ner_rus_bert.open(encoding='utf8') as f:
#         ner_config = json.load(f)
#     ner_config['metadata']['variables']['ROOT_PATH'] = '.\deeppavlov_data'
#
#     ner_model = build_model(ner_config, download=True)
    ner_model = build_model('ner_rus_bert', download=True, install=True)

    tokens = []
    for words, labels in zip(ner_model(text)[0], ner_model(text)[1]):
        for token, label in zip(words, labels):
            if label != "O":
                tokens.append(token)
    return tokens

# Natasha

def analyzes_natasha_ner(text):
    segmenter = Segmenter()

    emb = NewsEmbedding()
    ner_tagger = NewsNERTagger(emb)

    tokens = []

    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_ner(ner_tagger)
    for ent in doc.spans:
        tokens.append(ent.text)

    return tokens

# sparknlp

def analyzes_spartlp_ner(text):
    spark = sparknlp.start()
    pipeline = PretrainedPipeline('entity_recognizer_sm', lang='ru')
    result = pipeline.annotate(text)
    return result['ner']

def main():
    dataset = load_data(DATA_PATH)
#     dataset = pd.DataFrame({'wb_descriptions': '''Универсальный фиксатор для бровей PÚSY Brow
#     Fix, добро пожаловать в удивительный мир косметики и ухода за вашими бровями! Гель пуси для
#     бровей с эффектом ламинирования 5 мл - идеальный выбор для надежной и долговременной фиксации.
#     Невидимый при нанесении, этот гель поможет вам создать безупречную укладку бровей. Благодаря
#     уникальному составу, включающему специальные питательные вещества, фиксатор для бровей способен
#     питать и укреплять волоски, придавая им здоровый и ухоженный вид. Вы никогда не подозревали,
#     насколько важна правильная фиксация и уход за бровями, пока не попробовали этот продукт.
#     Фиксируйте свои брови с уверенностью!'''})

    # xlm-roberta
    dataset = CustomDataset(dataset)
    device = 'cpu'
    batch_size = 1
    max_length = 120
    model = "FacebookAI/xlm-roberta-large-finetuned-conll03-english"
    pipeline = LLMPipeline(model, dataset, batch_size, device)
    res = pipeline.infer_sample(next(iter(dataset)))
    predictions_df = pipeline.infer_dataset()
    print(predictions_df["predictions"])

#     for text in dataset['wb_descriptions']:
# #         print(analyzes_stanza_ner(text))
# #         analyzes_deeppavlov_ner(text)
# #         print(analyzes_natasha_ner(text))
# #         print()
# #         print(analyzes_spartlp_ner(text))
#
#
#
#
#
#     # Stanza


if __name__ == "__main__":
    main()
