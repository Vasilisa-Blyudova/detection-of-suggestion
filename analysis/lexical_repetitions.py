import pandas as pd
from pylats import lats
from taaled import ld

from config.constants import DATA_PATH


def load_data(path, format="csv"):
    if format == 'csv':
        data = pd.read_csv(path)
    else:
        data = pd.read_excel(path, engine="openpyxl")
    return data


def change_param():
    new_params = lats.parameters()
    new_params.model = "ru_core_news_sm"
    new_params.nlp = lats.load_model(new_params.model)

    return new_params


def calculate_ttr_index(text):
    clnsmpl = lats.Normalize(text, params=change_param())  # see pylats documentation for more information on the parameters file
    # print(clnsmpl.toks[:10])
    # print(clnsmpl.toks) #check sample output
    ldvals = ld.lexdiv(clnsmpl.toks)
    # print(ldvals.mattr)  # moving average TTR value
    # # print(ldvals.mattrs)
    # print(ldvals.ttr)
    # print(ldvals.rttr)
    # print(ldvals.rttr)
    # print(ldvals.maas)

    return ldvals.mattr


def main():
    dataset = load_data(DATA_PATH)

    for text in dataset["wb_descriptions"][:1]:
        print(calculate_ttr_index(text))


if __name__ == "__main__":
    main()
