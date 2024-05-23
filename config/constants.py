"""
Useful constant variables
"""

from pathlib import Path

# Project
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_PATH = PROJECT_ROOT / 'assets'
UTILS_DIR = PROJECT_ROOT / 'core_utils'

# Data
DATA_PATH = PROJECT_ROOT / 'dataset.csv'

# Crawler
CRAWLER_DICTIONARY_CONFIG_PATH = PROJECT_ROOT / 'scrapper_dict_config.json'
URL = 'https://dic.academic.ru'

# Dictionaries
ANTONYMS_DICT = ASSETS_PATH / 'dictionaries'/ 'antonyms_dictionary.csv'
PHRASEOLOGICAL_UNITS_DICT = ASSETS_PATH / 'dictionaries'/ 'phraseological_units_dictionary.csv'
SCECIFIC_WORDS_DICT = ASSETS_PATH / 'dictionaries'/ 'phraseological_units_dictionary.csv'

# Models
LOANWORDS_MODEL_WEIGHTS = UTILS_DIR / 'loanwords_model_weights'

# Weights
WEIGHTS = ASSETS_PATH / 'significance_weights.json'
