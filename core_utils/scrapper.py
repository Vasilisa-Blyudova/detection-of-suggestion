from abc import ABC, abstractmethod


class AbstractBaseCrawler(ABC):


    def __init__(self, config) -> None:

        self._config = config
        self.urls = []

    @abstractmethod
    def _extract_url(self, article_bs) -> str:
        pass

    @abstractmethod
    def find_features(self) -> None:
        pass

    @property
    def get_search_urls(self) -> list:
        return self._config.get_seed_urls()