from config.common import load_data, analyzes_pymorphy, analyzes_spacy, analyzes_stanza, analyzes_natasha
from config.constants import DATA_PATH


def main():
    dataset = load_data(DATA_PATH)

    for id, text in enumerate(dataset['wb_descriptions']):
        print(f"{id}----------------------------------------------")
        print("Превосходная степень прилагательных")
        print("result: ", analyzes_pymorphy(text, "ADJF", "Supr"))
        print("result: ", analyzes_spacy(text=text, pos="ADJ", tag_name="Degree", tag_value="Sup"))
        print("result: ", analyzes_stanza(text=text, pos="ADJ", tag="Degree=Sup"))
        print("result: ", analyzes_natasha(text=text, pos="ADJ", tag_name="Degree", tag_value="Sup"))
        print("Сравнительная степень прилагательных")
        print("result: ", analyzes_pymorphy(text, "ADJF", "Cmp2"))
        print("result: ", analyzes_spacy(text=text, pos="ADJ", tag_name="Degree", tag_value="Cmp"))
        print("result: ", analyzes_stanza(text=text, pos="ADJ", tag="Degree=Cmp"))
        print("result: ", analyzes_natasha(text=text, pos="ADJ", tag_name="Degree", tag_value="Cmp"))


if __name__ == "__main__":
    main()
