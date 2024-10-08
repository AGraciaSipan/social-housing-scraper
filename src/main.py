import logging
import os
from datetime import datetime

from utils.floors_price_scraper import FloorsPriceScraper
from utils.web_scraper import WebScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

WEB_URL = "https://www.femciutat.cat/promocions-actuals/viladecans-central-placa"
PDF_URL = "https://www.femciutat.cat/storage/uploads/viladecans-central-placa/02%20COST%20HAB%20reserva%20vila%202.pdf"

COLS = [
    "ID",
    "Planta",
    "Porta",
    "Dormitoris",
    "Adjudicat",
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
    "Superfície Interior (m2)",
    "Superfície Exterior (m2)",
    "Superfície Total (m2)",
    "Planta Parking",
    "ID Parking",
    "Superfície Parking (m2)",
    "Planta Traster",
    "ID Traster",
    "Superfície Traster (m2)",
    "ID Parking Moto",
    "Preu",
    "IVA",
    "Preu + IVA",
    "Fins Claus",
    "Juny 2024",
    "Plànol",
]


def main():
    output_dir = "output_files"
    os.makedirs(output_dir, exist_ok=True)

    web_scraper = WebScraper(WEB_URL)
    web_df = web_scraper.scrape_table()
    floors_price_scraper = FloorsPriceScraper(PDF_URL)
    prices_df = floors_price_scraper.scrape_floors_price()

    merged_df = web_df.merge(prices_df, on="ID", suffixes=("", "_drop"))

    filename = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    file_path = os.path.join(output_dir, filename)

    merged_df[COLS].to_csv(file_path, index=False, encoding="utf-8-sig")
    logging.info(f"Data saved to {filename}")


if __name__ == "__main__":
    main()
