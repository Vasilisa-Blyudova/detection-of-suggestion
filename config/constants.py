"""
Useful constant variables
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / 'dataset.csv'
ASSETS_PATH = PROJECT_ROOT / 'assets'
CRAWLER_CONFIG_PATH = PROJECT_ROOT / 'antonyms_detection_config.json'
URL = 'https://dic.academic.ru'