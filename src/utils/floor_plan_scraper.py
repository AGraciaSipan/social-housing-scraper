import logging
import re
from io import BytesIO

import pypdf

from utils.scraper import Scraper

PDF_PATTERNS = {
    "AP. PAS": re.compile(r"AP\. PAS (\d+,\d+) m²"),
    "AP. REBEDOR": re.compile(r"AP\. REBEDOR (\d+,\d+) m²"),
    "CH. CAMBRA HIGIÈNICA 1": re.compile(r"CH\. CAMBRA HIGIÈNICA 1 (\d+,\d+) m²"),
    "CH. CAMBRA HIGIÈNICA 2": re.compile(r"CH\. CAMBRA HIGIÈNICA 2 (\d+,\d+) m²"),
    "E-M-C. ESTAR-MENJADOR-CUINA": re.compile(r"E-M-C\. ESTAR-MENJADOR-CUINA (\d+,\d+) m²"),
    "H. HABITACIÓ 1": re.compile(r"H\. HABITACIÓ 1 (\d+,\d+) m²"),
    "H. HABITACIÓ 2": re.compile(r"H\. HABITACIÓ 2 (\d+,\d+) m²"),
    "H. HABITACIÓ 3": re.compile(r"H\. HABITACIÓ 3 (\d+,\d+) m²"),
    "S. SAFAREIG": re.compile(r"S\. SAFAREIG (\d+,\d+) m²"),
    "T. TERRASSA": re.compile(r"T\. TERRASSA (\d+,\d+) m²"),
    "B. BALCÓ": re.compile(r"B\. BALCÓ (\d+,\d+) m²"),
}


class FloorPlanScraper:
    def __init__(self, url):
        self.scraper = Scraper(url)

    def scrape_floor_plan(self):
        content = self.scraper.fetch_content()
        if content:
            try:
                reader = pypdf.PdfReader(BytesIO(content))
                page_text = reader.get_page(0).extract_text()

                data = {}
                for key, pattern in PDF_PATTERNS.items():
                    match = pattern.search(page_text)
                    data[key] = float(match.group(1).replace(",", ".")) if match else None

                return data
            except pypdf.errors.PdfReadError as e:
                logging.error(f"Error reading PDF data from {self.scraper.url}: {e}")
                return {key: None for key in PDF_PATTERNS.keys()}
        else:
            logging.error("Failed to fetch PDF content.")
            return {key: None for key in PDF_PATTERNS.keys()}
