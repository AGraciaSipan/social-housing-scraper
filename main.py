import logging
import os
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

URL = "https://www.femciutat.cat/promocions-actuals/viladecans-central-placa"
COLUMNS_MAP = {"": "ID", "Superfície": "Superfície (m2)", "Adjudicació": "Adjudicat"}


def fetch_page_content(url):
    """Fetches the content of the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None


def scrape_flats_data(content):
    """Scrapes the flats data from the HTML content."""
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


def transform_df(df):
    """Transforms the DataFrame with appropriate data types and column names."""
    df["Dormitoris"] = df["Dormitoris"].str.replace(" dorm", "").astype(int)
    df["Superfície"] = df["Superfície"].str.replace("m2", "").astype(float)
    df["Adjudicació"] = df["Adjudicació"].map({"No Adjudicat": False, "Adjudicat": True}).astype(bool)
    df.rename(columns=COLUMNS_MAP, inplace=True)

    return df


def main():
    output_dir = "output_files"
    os.makedirs(output_dir, exist_ok=True)

    content = fetch_page_content(URL)

    if content:
        df = scrape_flats_data(content)
        df = transform_df(df)

        filename = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        file_path = os.path.join(output_dir, filename)

        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        logging.info(f"Data saved to {filename}")
        print(df)


if __name__ == "__main__":
    main()
