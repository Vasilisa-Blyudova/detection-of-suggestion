import pandas as pd


def load_data(path, file_format="csv"):
    if file_format == 'csv':
        data = pd.read_csv(path)
    else:
        data = pd.read_excel(path, engine="openpyxl")
    return data
