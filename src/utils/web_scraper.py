import logging

import pandas as pd
from bs4 import BeautifulSoup

from utils.floor_plan_scraper import FloorPlanScraper
from utils.scraper import Scraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

INT_COLS = ["", "Dormitoris"]
FLOAT_COLS = [
    "Superfície",
    "AP. PAS",
    "AP. REBEDOR",
    "CH. CAMBRA HIGIÈNICA 1",
    "CH. CAMBRA HIGIÈNICA 2",
    "E-M-C. ESTAR-MENJADOR-CUINA",
    "H. HABITACIÓ 1",
    "H. HABITACIÓ 2",
    "H. HABITACIÓ 3",
    "S. SAFAREIG",
    "T. TERRASSA",
    "B. BALCÓ",
]
COLUMNS_MAP = {"": "ID", "Superfície": "Superfície (m2)", "Adjudicació": "Adjudicat"}


class WebScraper(Scraper):
    def __init__(self, url):
        super().__init__(url)

    @staticmethod
    def _scrape_html_content(content):
        """Scrapes the table data from the HTML content."""
        soup = BeautifulSoup(content, "html.parser")
        table = soup.find("table")

        headers = [th.text.strip() for th in table.find("thead").find_all("th")]
        rows = []

        for tr in table.find("tbody").find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            pdf_link = tr.find("a", {"class": "link link--download"})
            pdf_url = pdf_link["href"] if pdf_link else None
            cells[-1] = pdf_url  # Replace the last element (empty string scraped searching 'td') with pdf_url
            rows.append(cells)

        df = pd.DataFrame(rows, columns=headers)
        return df

    @staticmethod
    def _scrape_pdf_content(df):
        """Adds data from PDFs to the DataFrame."""
        for index, row in df.iterrows():
            pdf_url = row["Plànol"]
            if pdf_url:
                floor_plan_scraper = FloorPlanScraper(pdf_url)
                pdf_data = floor_plan_scraper.scrape_floor_plan()
                for key, value in pdf_data.items():
                    df.at[index, key] = value
        return df

    @staticmethod
    def _transform_df(df):
        """Transforms the DataFrame with appropriate data types and column names."""
        df["Dormitoris"] = df["Dormitoris"].str.replace(" dorm", "")
        df["Superfície"] = df["Superfície"].str.replace("m2", "")

        for col in INT_COLS:
            df[col] = df[col].astype(int)

        for col in FLOAT_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df["Adjudicació"] = df["Adjudicació"].map({"No Adjudicat": False, "Adjudicat": True}).astype(bool)
        df.rename(columns=COLUMNS_MAP, inplace=True)

        return df

    def scrape_table(self):
        """Fetches the content of the URL and scrapes the table data."""
        content = self.fetch_content()
        if content:
            df = self._scrape_html_content(content)
            df = self._scrape_pdf_content(df)
            return self._transform_df(df)
        else:
            logging.error("Failed to fetch content.")
            return None
