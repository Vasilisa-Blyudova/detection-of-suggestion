from pylats import lats
from taaled import ld

from config.common import load_data
from config.constants import DATA_PATH


def change_param():
    new_params = lats.parameters()
    new_params.model = "ru_core_news_lg"
    new_params.nlp = lats.load_model(new_params.model)

    return new_params


def calculate_mattr_index(text):
    clnsmpl = lats.Normalize(text, params=change_param())
    ldvals = ld.lexdiv(clnsmpl.toks)

    return ldvals.mattr


def main():
    dataset = load_data(DATA_PATH)

    for text in dataset["wb_descriptions"]:
        print(calculate_mattr_index(text))


if __name__ == "__main__":
    main()
