from config.common import load_data, analyzes_pymorphy, analyzes_spacy, analyzes_stanza, analyzes_natasha
from config.constants import DATA_PATH


def main():
    dataset = load_data(DATA_PATH)

    for id, text in enumerate(dataset['wb_descriptions'][:2]):
        print(f"{id}-----------------------------------------------------------------")
        print(analyzes_pymorphy(text, tag="pssv"))
        print(analyzes_spacy(text, tag_name="Voice", tag_value="Pass"))
        print(analyzes_stanza(text, tag="Voice=Pass"))
        print(analyzes_natasha(text, tag_name="Voice", tag_value="Pass"))


if __name__ == "__main__":
    main()
