from analysis.preprocessor import Preprocessor
from config.common import load_data
from config.constants import ASSETS_PATH, DATA_PATH


def detect_phraseological_units(phraseological_units_dictionary, text):
    common_unit = []
    for phraseological_unit in phraseological_units_dictionary["phraseological_units"].values:
        if phraseological_unit in ' '.join(text):
            common_unit.append(phraseological_unit)
    return common_unit


def main():
    dataset = load_data(DATA_PATH)
    phraseological_units_dictionary = load_data(ASSETS_PATH / "phraseological_units_dictionary.csv")

    preprocessor = Preprocessor(dataset['wb_descriptions'])
    preprocessor.lemmatize()
    lemmatized_texts = preprocessor.get_lemmatizing()

    for text in lemmatized_texts[:5]:
        print(detect_phraseological_units(phraseological_units_dictionary, text))


if __name__ == "__main__":
    main()
