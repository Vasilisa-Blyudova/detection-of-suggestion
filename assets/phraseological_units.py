import json
import re
import time
# import request
from pathlib import Path
from typing import Pattern, Union
from urllib.parse import urljoin

import pandas as pd
import requests
from antonyms import make_request
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib3 import Retry

from config.constants import CRAWLER_CONFIG_PATH, URL
from core_utils.config_dto import ConfigDTO
from core_utils.scrapper import AbstractBaseCrawler


class Config:
    seed_urls: list[str]
    total_articles_to_find_and_parse: int
    headers: dict[str, str]
    encoding: str
    timeout: int
    verify_certificate: bool
    headless_mode: bool

    def __init__(self, path_to_config: Path) -> None:
        self.path_to_config = path_to_config
        config = self._extract_config_content()
        self._seed_urls = config.seed_urls
        self._headers = config.headers
        self._num_articles = config.total_articles
        self._headers = config.headers
        self._encoding = config.encoding
        self._timeout = config.timeout

    def _extract_config_content(self) -> ConfigDTO:
        with open(self.path_to_config, encoding="utf-8") as file:
            config = json.load(file)

        return ConfigDTO(seed_urls=config['seed_urls'],
                         headers=config['headers'],
                         total_descriptions_to_find_and_parse=
                         config['total_descriptions_to_find_and_parse'],
                         encoding=config['encoding'],
                         timeout=config['timeout'])

    def get_seed_urls(self) -> list[str]:
        return self._seed_urls

    def get_num_descriptions(self) -> int:
        return self._num_articles

    def get_headers(self) -> dict[str, str]:
        return self._headers

    def get_encoding(self) -> str:
        return str(self._encoding)

    def get_timeout(self) -> int:
        return int(self._timeout)


class BaseCrawlerPhraseologicalUnits(AbstractBaseCrawler):
    """
    Crawler implementation
    """

    def __init__(self, config: Config) -> None:

        self._config = config
        self.urls = []
        self.phraseological_units = []

    def _extract_url(self, article_bs) -> str:
        return article_bs.find('a').get('href')

    def find_features(self) -> None:
        request = make_request(self._config.get_seed_urls()[1], self._config)
        if not request.ok:
            print(f'Error: {request.status_code} {self._config.get_seed_urls()[1]}', flush=True)
        time.sleep(2)

        soup = BeautifulSoup(request.text, features='html.parser')

        articles = soup.find('div', class_='contents-wrap').find_all('li')

        for item in articles:
            if len(self.urls) == self._config.get_num_descriptions():
                break
            url = self._extract_url(item)
            full_url_ = urljoin(self._config.get_seed_urls()[1], url)
            if full_url_ not in self.urls:
               self.urls.append(full_url_)

    def find_phraseological_units(self):
        for url in self.urls:
            request = make_request(url, self._config)
            if not request.ok:
                print(f'Error: {request.status_code} {self._config.get_seed_urls()[0]}', flush=True)
                continue
            time.sleep(1)

            soup = BeautifulSoup(request.text, features='html.parser')

            phrases = soup.find('div', class_='terms-wrap').find_all('li')
            for phrase in phrases:
                self.phraseological_units.append(phrase.text)

    def get_dictionary(self):
        dictionary = pd.DataFrame({'phraseological_units': self.phraseological_units})
        return dictionary.to_csv(Path('D:\Документы\ВКР\detection-of-suggestion\\assets\phraseological_units_dictionary.csv'), index=False)




if __name__ == "__main__":
    config = Config(CRAWLER_CONFIG_PATH)
    crawler = BaseCrawlerPhraseologicalUnits(config)
    crawler.find_features()
    crawler.find_phraseological_units()
    dictionary = crawler.get_dictionary()