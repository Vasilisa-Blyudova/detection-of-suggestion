from pathlib import Path

import pandas as pd
from pylats import lats
from taaled import ld

# def calculate_ttr_index(unique_words, words):
#     pass

def main():
    dataset = pd.read_csv(Path('D:\Документы\ВКР\detection-of-suggestion\data.csv'))
#     data_preprocessor = Preprocess(dataset['wb_descriptions'][:1])
#     data_preprocessor.tokenize()
#     data_preprocessor.lemmatize()
#     unique_words = data_preprocessor.get_unique_words()
#     non_unique_words = data_preprocessor.remove_functional_pos()
#     print(unique_words)
#     print(non_unique_words)
    new_params = lats.parameters()
    new_params.model = "ru_core_news_sm"
    new_params.nlp = lats.load_model(new_params.model)
    clnsmpl = lats.Normalize(dataset['wb_descriptions'][0], params=new_params) #see pylats documentation for more information on the parameters file
#     print(clnsmpl.toks) #check sample output
    ldvals = ld.lexdiv(clnsmpl.toks)
    print(ldvals.mattr) #moving average TTR value
#     print(ldvals.mattrs)
    print(ldvals.ttr)
    print(ldvals.rttr)
    print(ldvals.rttr)
    print(ldvals.maas)
    print(dir(ldvals))


if __name__ == "__main__":
    main()