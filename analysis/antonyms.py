from analysis.preprocessor import Preprocessor
from config.common import load_data
from config.constants import DATA_PATH, ANTONYMS_DICT


def detect_antonyms(text):
    antonyms_dict = {}
    antonyms_dictionary = load_data(ANTONYMS_DICT)
    for word in text:
        if not antonyms_dictionary.loc[(antonyms_dictionary["term"] == word)].empty:
            antonyms = antonyms_dictionary.loc[(antonyms_dictionary["term"] == word), "antonyms"].values[0]
            for antonym in antonyms.split(", "):
                if antonym in " ".join(text):
                    antonyms_dict[word] = antonym
    return list(antonyms_dict.items())


def main():
    dataset = load_data(DATA_PATH)

    preprocessor = Preprocessor(dataset['wb_descriptions'][:25])
    preprocessor.lemmatize()
    lemmatized_texts = preprocessor.get_lemmatizing()

    for id, text in enumerate(lemmatized_texts):
        print(f"{id}------------------------------------")
        print(detect_antonyms(text))


if __name__ == "__main__":
    main()
