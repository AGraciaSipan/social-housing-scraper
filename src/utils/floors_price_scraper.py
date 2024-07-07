import logging
import re
from io import BytesIO

import pandas as pd
import tabula

from utils.scraper import Scraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

HEADERS = [
    "ID",
    "Planta",
    "Porta",
    "Superfície Interior (m2)",
    "Superfície Exterior (m2)",
    "Superfície Total (m2)",
    "Superfície Protegida (m2)",
    "Planta Parking",
    "ID Parking",
    "Superfície Parking (m2)",
    "Planta Traster",
    "ID Traster",
    "Superfície Traster (m2)",
    "Planta Parking Moto",
    "ID Parking Moto",
    "Superfície Parking Moto (m2)",
    "Preu",
    "IVA",
    "Preu + IVA",
    "Hipoteca",
    "Fins Claus",
    "Juny 2024",
    "Març 2025",
    "Setembre 2025",
    "Març 2026",
    "Setembre 2026",
    "Març 2027",
    "Lliurament",
    "Quota Hipoteca (+2,50%)",
    "Ingressos Nets Mínims",
]

MISSING_HEADERS = ["Planta Parking Moto", "ID Parking Moto", "Superfície Parking Moto (m2)"]
START_INDEX_MISSING = HEADERS.index(MISSING_HEADERS[0])
EXPECTED_COL_COUNT = len(HEADERS)
EXPECTED_COL_COUNT_W_MISSING_HEADERS = EXPECTED_COL_COUNT - len(MISSING_HEADERS)

FLOAT_COLS = [
    "Superfície Interior (m2)",
    "Superfície Exterior (m2)",
    "Superfície Total (m2)",
    "Superfície Protegida (m2)",
    "Superfície Parking (m2)",
    "Superfície Traster (m2)",
    "Superfície Parking Moto (m2)",
    "Preu",
    "IVA",
    "Preu + IVA",
    "Hipoteca",
    "Fins Claus",
    "Juny 2024",
    "Març 2025",
    "Setembre 2025",
    "Març 2026",
    "Setembre 2026",
    "Març 2027",
    "Lliurament",
    "Quota Hipoteca (+2,50%)",
    "Ingressos Nets Mínims",
]


class FloorsPriceScraper(Scraper):
    def __init__(self, url):
        super().__init__(url)

    @staticmethod
    def _process_table(table):
        if table.shape[1] == EXPECTED_COL_COUNT:
            table.columns = HEADERS
        elif table.shape[1] == EXPECTED_COL_COUNT_W_MISSING_HEADERS:
            for idx, col_name in enumerate(MISSING_HEADERS, start=START_INDEX_MISSING):
                table.insert(idx, col_name, pd.NA)
            table.columns = HEADERS
        else:
            logging.warning(f"Table with unexpected number of columns: {table.shape[1]}")
            return None
        return table

    def _transform_df(self, df):
        for col in FLOAT_COLS:
            df[col] = df[col].apply(self._normalize_floats)
        return df

    @staticmethod
    def _normalize_floats(value):
        if pd.isna(value):
            return None
        value = re.sub(r"[^\d,.-]", "", value)
        value = value.replace(".", "").replace(",", ".")
        try:
            return float(value)
        except ValueError:
            return None

    def scrape_floors_price(self):
        content = self.fetch_content()
        if not content:
            logging.error("Failed to fetch PDF content.")
            return pd.DataFrame()

        try:
            tables = tabula.read_pdf(
                BytesIO(content), pages="all", multiple_tables=True, pandas_options={"header": None}
            )
            logging.info(f"Extracted {len(tables)} tables from the PDF.")
        except Exception as e:
            logging.error(f"Failed to read tables from PDF: {e}")
            return pd.DataFrame()

        relevant_tables = [self._process_table(table) for table in tables if table is not None]

        if relevant_tables:
            concatenated_df = pd.concat(relevant_tables, axis=0, ignore_index=True)
            logging.info("Successfully concatenated relevant tables into a single DataFrame.")
        else:
            concatenated_df = pd.DataFrame()
            logging.info("No relevant tables found in the PDF.")

        return self._transform_df(concatenated_df)
