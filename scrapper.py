import json
import time
# import request
from pathlib import Path
from typing import Union, Pattern

import pandas as pd
import requests

from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib3 import Retry

from config.constants import CRAWLER_CONFIG_PATH, URL
from core_utils.config_dto import ConfigDTO


class Config:
    """
    Unpacks and validates configurations
    """

    seed_urls: list[str]
    total_articles_to_find_and_parse: int
    headers: dict[str, str]
    encoding: str
    timeout: int
    verify_certificate: bool
    headless_mode: bool

    def __init__(self, path_to_config: Path) -> None:
        """
        Initializes an instance of the Config class
        """

        self.path_to_config = path_to_config
        config = self._extract_config_content()
        self._seed_urls = config.seed_urls
        self._headers = config.headers
        self._num_articles = config.total_articles
        self._headers = config.headers
        self._encoding = config.encoding
        self._timeout = config.timeout

    def _extract_config_content(self) -> ConfigDTO:
        """
        Returns config values
        """
        with open(self.path_to_config, encoding="utf-8") as file:
            config = json.load(file)

        return ConfigDTO(seed_urls=config['seed_urls'],
                         headers=config['headers'],
                         total_descriptions_to_find_and_parse=
                         config['total_descriptions_to_find_and_parse'],
                         encoding=config['encoding'],
                         timeout=config['timeout'])

    def get_seed_urls(self) -> list[str]:
        """
        Retrieve seed urls
        """
        return self._seed_urls

    def get_num_descriptions(self) -> int:
        """
        Retrieve total number of articles to scrape
        """
        return self._num_articles

    def get_headers(self) -> dict[str, str]:
        """
        Retrieve headers to use during requesting
        """
        return self._headers

    def get_encoding(self) -> str:
        """
        Retrieve encoding to use during parsing
        """
        return str(self._encoding)

    def get_timeout(self) -> int:
        """
        Retrieve number of seconds to wait for response
        """
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


class BaseCrawler:
    """
    Crawler implementation
    """

    url_pattern: Union[Pattern, str]

    def __init__(self, config: Config) -> None:
        """
        Initializes an instance of the BaseCrawler class
        """

        self._config = config
        self._urls = []
        self.vendor_codes = []

    def _extract_url(self, vendor_code: str) -> str:
        """
        Finds and retrieves URL
        """
        return f"{URL}catalog/{vendor_code}/detail.aspx"

    def find_vendor_code(self) -> None:
        """
        Finds vendor code for all products
        """
        for seed_url in self._config.get_seed_urls():
            response = make_request(seed_url, self._config)
            if not response.ok:
                print(f'Error: {response.status_code} {seed_url}', flush=True)
                continue

            response = response.json()

            products = response['data']['products']
            for product in products:
                self.vendor_codes.append(str(product['id']))

    def collect_urls(self):
        for vendor_code in self.vendor_codes:
            if len(self._urls) == self._config.get_num_descriptions():
                break
            url = self._extract_url(vendor_code)
            self._urls.append(url)


    def get_urls(self):
        return self._urls

    def get_search_urls(self) -> list:
        """
        Returns seed_urls param
        """
        return self._config.get_seed_urls()


class ChromeDriverMixIn:
    """
    Service class providing chrome webdriver services for crawling
    """

    def __init__(self, headless: bool = True) -> None:
        """
        Initializes an instance of the ChromeDriverMixIn class
        """

        self._headless = headless
        self.driver = self._init_driver()

    def _init_driver(self) -> webdriver.Chrome:
        """
        Initializes chrome webdriver
        """
        options = Options()
        if self._headless:
            options.add_argument('--headless')
        return webdriver.Chrome(options=options)


class ClickDescription(BaseCrawler, ChromeDriverMixIn):
    """
    Crawler with webdriver for dynamic sites with button clicking
    """

    def __init__(self, config: Config):
        """
        Initializes an instance of the ClickCrawler class
        """

        BaseCrawler.__init__(self, config=config)
        ChromeDriverMixIn.__init__(self)

    def find_description(self, url: str) -> str:
        """
        Finds description of product
        """
        self.driver.get(url)
        self.click_page()
        description = WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'option__text')))

        return description.text

    def click_page(self) -> None:
        """
        Service method implementing button clicks
        """
        button = WebDriverWait(self.driver, 2).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'product-page__btn-detail')))
        button.send_keys(Keys.RETURN)
        time.sleep(2)


if __name__ == "__main__":
    config = Config(CRAWLER_CONFIG_PATH)
    crawler = BaseCrawler(config)
    crawler.find_vendor_code()
    crawler.collect_urls()
    urls = crawler.get_urls()
    click = ClickDescription(config)
    descriptions = []
    for url in urls:
        descriptions.append(click.find_description(url))

    df = pd.DataFrame({'wb_descriptions': descriptions}).to_csv('data.csv')
