import json
import re
import time
# import request
from pathlib import Path
from typing import Pattern, Union
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib3 import Retry

from config.constants import ANTONYMS_DICT, CRAWLER_DICTIONARY_CONFIG_PATH, URL
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


def make_request(url: str, config: Config) -> requests.models.Response:
    """
    Delivers a response from a request
    with given configuration
    """
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    response = session.get(url,
                           headers=config.get_headers(),
                           timeout=config.get_timeout())
    response.encoding = config.get_encoding()
    return response


class BaseCrawlerAntonyms(AbstractBaseCrawler):
    """
    Crawler implementation
    """

    def __init__(self, config: Config) -> None:

        self._config = config
        self.urls = []
        self.terms_url = []
        self.terms = []
        self.antonyms = []

    def _extract_url(self, article_bs) -> str:
        return article_bs.find('a').get('href')

    def find_features(self) -> None:
        request = make_request(self._config.get_seed_urls()[0], self._config)
        if not request.ok:
            print(f'Error: {request.status_code} {self._config.get_seed_urls()[0]}', flush=True)
        time.sleep(2)

        soup = BeautifulSoup(request.text, features='html.parser')

        articles = soup.find('div', class_='contents-wrap').find_all('li')

        for item in articles:
            if len(self.urls) == self._config.get_num_descriptions():
                break
            url = self._extract_url(item)
            full_url_ = urljoin(self._config.get_seed_urls()[0], url)
            if full_url_ not in self.urls:
                self.urls.append(full_url_)

    def find_terms(self):
        for url in self.urls:
            request = make_request(url, self._config)
            if not request.ok:
                print(f'Error: {request.status_code} {self._config.get_seed_urls()[0]}', flush=True)
                continue
            time.sleep(1)

            soup = BeautifulSoup(request.text, features='html.parser')

            terms = soup.find('div', class_='terms-wrap').find_all('li')
            #             print(url)
            more_terms = soup.find('ul', class_='arrow')
            if not more_terms:
                continue
            terms.extend(self.find_more_terms(more_terms.find('li')))
            if not terms:
                continue
            for term in terms:
                self.terms.append(term.text)
                url = self._extract_url(term)
                full_url_ = urljoin(self._config.get_seed_urls()[0], url)
                self.terms_url.append(full_url_)

    def find_more_terms(self, more_terms):
        if 'следующая' in more_terms.text:
            more_terms_url = self._extract_url(more_terms)
            full_url_ = urljoin(self._config.get_seed_urls()[0], more_terms_url)
            request = make_request(full_url_, self._config)
            soup = BeautifulSoup(request.text, features='html.parser')

            new_terms = soup.find('div', class_='terms-wrap').find_all('li')

        return new_terms

    def find_antonyms(self):
        for term_url in self.terms_url:
            print(term_url)
            request = make_request(term_url, self._config)
            if not request.ok:
                print(f'Error: {request.status_code} {self._config.get_seed_urls()[0]}', flush=True)
                continue
            time.sleep(1)

            soup = BeautifulSoup(request.text, features='html.parser')

            antonyms = soup.find('div', class_='content').find_all('div', class_='tags_list')
            if not antonyms:
                self.antonyms.append([])
                continue
            self.antonyms.append(antonyms[-1].text)

    def get_dictionary(self):
        dictionary = pd.DataFrame({'term': self.terms, 'antonyms': self.antonyms})
        return dictionary.to_csv(ANTONYMS_DICT,
                                 index=False)


if __name__ == "__main__":
    #     config = Config(CRAWLER_CONFIG_PATH)
    #     crawler = BaseCrawlerAntonyms(config)
    #     crawler.find_features()
    #     crawler.find_terms()
    #     crawler.find_antonyms()
    #     dictionary = crawler.get_dictionary()
    pass
