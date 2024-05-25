import pandas as pd
import stanza
import torch
from deeppavlov import build_model
from natasha import Doc, NewsEmbedding, NewsNERTagger, Segmenter
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, XLMRobertaForTokenClassification

from config.common import load_data
from config.constants import DATA_PATH


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
    nlp = stanza.Pipeline(lang='ru', processors='tokenize,ner', download_method=None)
    doc = nlp(text)

    tokens = []

    for token in doc.ents:
        tokens.append(token.text)

    return tokens


# Deep Pavlov

def analyzes_deeppavlov_ner(text):
    text = [text]
    # with configs.ner.ner_rus_bert.open(encoding='utf8') as f:
    #     ner_config = json.load(f)
    # ner_config['metadata']['variables']['ROOT_PATH'] = '..\deeppavlov'
    #
    # ner_model = build_model(ner_config, download=True)
    ner_model = build_model("ner_rus_bert", download=True, install=True)

    tokens = []
    for words, labels in zip(ner_model(text)[0], ner_model(text)[1]):
        # print(ner_model(text)[0])
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


def main():
    dataset = load_data(DATA_PATH)

    # xlm-roberta
    dataset = CustomDataset(dataset)
    device = 'cpu'
    batch_size = 1
    model = "FacebookAI/xlm-roberta-large-finetuned-conll03-english"
    pipeline = LLMPipeline(model, dataset, batch_size, device)
    # res = pipeline.infer_sample(next(iter(dataset)))
    predictions_df = pipeline.infer_dataset()
    print(predictions_df["predictions"])

    for id, text in enumerate(dataset['wb_descriptions']):
        print(f"{id}----------------------------------------")
        # stanza
        print(analyzes_stanza_ner(text))
        # deeppavlov
        print(analyzes_deeppavlov_ner(text))
        # natasha
        print(analyzes_natasha_ner(text))


if __name__ == "__main__":
    main()
