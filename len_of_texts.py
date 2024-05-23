from pathlib import Path

import nltk
import pandas as pd
import pymorphy2
import spacy
from nltk.tokenize import word_tokenize

from analysis.preprocessor import Preprocessor
from config.constants import ASSETS_PATH, DATA_PATH


def load_data(path, format="csv"):
    if format == 'csv':
        data = pd.read_csv(path)
    else:
        data = pd.read_excel(path, engine="openpyxl")
    return data


def main():
    dataset = load_data(DATA_PATH)

    dataset = dataset['wb_descriptions']
    len_of_text = []
    for text in dataset:
        len_of_text.append(len(text.split()))

    print(len_of_text)
    print(sum(len_of_text) / len(len_of_text))
    print(sum(len_of_text))


if __name__ == "__main__":
    main()
