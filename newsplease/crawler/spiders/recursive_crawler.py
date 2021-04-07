import logging

import scrapy
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs


class RecursiveCrawler(scrapy.Spider):
    name = "RecursiveCrawler"
    allowed_domains = None
    start_urls = None
    original_url = None

    log = None

    config = None
    helper = None

    ignore_regex = None
    ignore_file_extensions = None

    def __init__(self, helper, url, config, ignore_regex, *args, **kwargs):
        self.log = logging.getLogger(__name__)

        self.config = config
        self.helper = helper

        self.ignore_regex = ignore_regex
        self.ignore_file_extensions = self.config.section(
            'Crawler')['ignore_file_extensions']

        self.original_url = url

        self.allowed_domains = [self.helper.url_extractor
                                    .get_allowed_domain(url)]
        self.start_urls = [self.helper.url_extractor.get_start_url(url)]

        super(RecursiveCrawler, self).__init__(*args, **kwargs)

    def parse(self, response):
        """
        Checks any given response on being an article and if positiv,
        passes the response to the pipeline.

        :param obj response: The scrapy response
        """
        if not self.helper.parse_crawler.content_type(response):
            return

        for request in self.helper.parse_crawler \
                .recursive_requests(response, self, self.ignore_regex,
                                    self.ignore_file_extensions):
            yield request
            
        # Remove tracking from urls    
        u = urlparse(self.original_url)
        query = parse_qs(u.query, keep_blank_values=True)
        query.pop('source', None)
        u = u._replace(query=urlencode(query, True))
        
        yield self.helper.parse_crawler.pass_to_pipeline_if_article(
            response, self.allowed_domains[0], urlunparse(u))

    @staticmethod
    def supports_site(url):
        """
        Recursive Crawler are supported by every site!

        Determines if this crawler works on the given url.

        :param str url: The url to test
        :return bool: Determines wether this crawler work on the given url
        """
        return True
