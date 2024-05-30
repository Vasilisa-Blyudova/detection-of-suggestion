"""
ConfigDTO class implementation: stores the configuration information
"""


class ConfigDTO:
    """
    Type annotations for configurations
    """

    seed_urls: list[str]
    total_articles: int
    headers: dict[str, str]
    encoding: str
    timeout: int

    def __init__(self,
                 seed_urls: list[str],
                 total_descriptions_to_find_and_parse: int,
                 headers: dict[str, str],
                 encoding: str,
                 timeout: int
                 ):
        """
        Initializes an instance of the ConfigDTO class
        """

        self.seed_urls = seed_urls
        self.total_articles = total_descriptions_to_find_and_parse
        self.headers = headers
        self.encoding = encoding
        self.timeout = timeout
