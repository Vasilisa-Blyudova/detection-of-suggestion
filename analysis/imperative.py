from analysis.preprocessor import Preprocessor
from config.common import load_data, analyzes_pymorphy, analyzes_spacy, analyzes_stanza, analyzes_natasha
from config.constants import DATA_PATH


def main():
    dataset = load_data(DATA_PATH)

    for id, text in enumerate(dataset['wb_descriptions'][3:4]):
        print(f"{id}--------------------------------------------------------------")
        print(analyzes_pymorphy(text, "VERB", "impr"))
        print(analyzes_spacy(text, "VERB", "Mood", "Imp"))
        print(analyzes_stanza(text, "VERB", "Mood=Imp"))
        print(analyzes_natasha(text, "VERB", "Mood", "Imp"))


if __name__ == "__main__":
    main()
