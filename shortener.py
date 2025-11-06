import requests
import logging
from config import *

logger = logging.getLogger(__name__)

class LinkShortener:
    def __init__(self):
        self.api_key = SHORTENER_API
        self.domain = SHORTENER_DOMAIN
        self.type = SHORTENER_TYPE
    
    def shorten(self, url: str) -> str:
        """
        Shorten URL using configured shortener service
        Returns shortened URL or original URL if shortening fails
        """
        try:
            if self.type == 'gplinks':
                return self._gplinks(url)
            elif self.type == '
