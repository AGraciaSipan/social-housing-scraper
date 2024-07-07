import logging

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Scraper:
    def __init__(self, url):
        self.url = url

    def fetch_content(self):
        """Fetches the content of the instance's URL."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logging.error(f"Error fetching URL {self.url}: {e}")
            return None
