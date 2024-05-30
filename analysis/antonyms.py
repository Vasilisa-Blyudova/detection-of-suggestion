from analysis.preprocessor import Preprocessor
from config.common import load_data
from config.constants import DATA_PATH, ANTONYMS_DICT


def detect_antonyms(antonyms_dictionary, text):
    antonyms_dict = {}
    for word in text:
        if not antonyms_dictionary.loc[(antonyms_dictionary["term"] == word)].empty:
            antonyms = antonyms_dictionary.loc[(antonyms_dictionary["term"] == word), "antonyms"].values[0]
            for antonym in antonyms.split(", "):
                if antonym in " ".join(text):
                    antonyms_dict[word] = antonym
    return antonyms_dict


def main():
    dataset = load_data(DATA_PATH)
    antonyms_dictionary = load_data(ANTONYMS_DICT)

    preprocessor = Preprocessor(dataset['wb_descriptions'][:25])
    preprocessor.lemmatize()
    lemmatized_texts = preprocessor.get_lemmatizing()

    for id, text in enumerate(lemmatized_texts):
        print(f"{id}------------------------------------")
        print(detect_antonyms(antonyms_dictionary, text))


if __name__ == "__main__":
    main()
