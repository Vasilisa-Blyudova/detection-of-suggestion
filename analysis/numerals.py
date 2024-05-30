from config.common import load_data, analyzes_pymorphy, analyzes_spacy, analyzes_stanza, analyzes_natasha
from config.constants import DATA_PATH


def main():
    dataset = load_data(DATA_PATH)

    for id, text in enumerate(dataset['wb_descriptions']):
        print(f"{id}----------------------------------------------")
        print(analyzes_pymorphy(text, ["NUMR", "NUMB", "Anum"]))
        print(analyzes_spacy(text, "NUM"))
        print(analyzes_stanza(text, "NUM"))
        print(analyzes_natasha(text, "NUM"))


if __name__ == "__main__":
    main()
