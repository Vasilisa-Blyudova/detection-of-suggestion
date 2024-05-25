from analysis.preprocessor import Preprocessor
from config.common import load_data
from config.constants import DATA_PATH, SCECIFIC_WORDS_DICT


def detect_specific_meaning(dictionary, text):
    common_words = []
    for word in text:
        if not dictionary.loc[(dictionary["слово"] == word) & (dictionary["рейтинг"] < 3), "рейтинг"].empty:
            common_words.append(word)
    return common_words


def main():
    dataset = load_data(DATA_PATH)
    specific_words_dictionary = load_data(SCECIFIC_WORDS_DICT, "xlsx")

    preprocessor = Preprocessor(dataset['wb_descriptions'])
    preprocessor.lemmatize()
    lemmatized_texts = preprocessor.get_lemmatizing()

    for text in lemmatized_texts[:5]:
        print(detect_specific_meaning(specific_words_dictionary, text))


if __name__ == "__main__":
    main()
