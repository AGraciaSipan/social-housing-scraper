import logging
import os
import re
from datetime import datetime
from io import BytesIO

import pandas as pd
import pypdf
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

URL = "https://www.femciutat.cat/promocions-actuals/viladecans-central-placa"
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
FLOAT_COLS = ["Superfície"] + list(PDF_PATTERNS.keys())
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
    df["Superfície"] = df["Superfície"].str.replace("m2", "")

    for col in FLOAT_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Adjudicació"] = df["Adjudicació"].map({"No Adjudicat": False, "Adjudicat": True}).astype(bool)
    df.rename(columns=COLUMNS_MAP, inplace=True)

    cols = df.columns.tolist()
    cols.remove("Plànol")
    cols.append("Plànol")

    return df[cols]


def extract_pdf_data(pdf_url):
    """Extracts data from the PDF at the given URL."""
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        reader = pypdf.PdfReader(BytesIO(response.content))
        page_text = reader.pages[0].extract_text()

        data = {}
        for key, pattern in PDF_PATTERNS.items():
            match = pattern.search(page_text)
            data[key] = float(match.group(1).replace(",", ".")) if match else None

        return data
    except (requests.RequestException, pypdf.errors.PdfReadError) as e:
        logging.error(f"Error extracting PDF data from {pdf_url}: {e}")
        return {key: None for key in PDF_PATTERNS.keys()}


def add_pdf_data_to_df(df):
    """Adds data from PDFs to the DataFrame."""
    for index, row in df.iterrows():
        pdf_url = row["Plànol"]
        if pdf_url:
            pdf_data = extract_pdf_data(pdf_url)
            for key, value in pdf_data.items():
                df.at[index, key] = value
    return df


def main():
    output_dir = "output_files"
    os.makedirs(output_dir, exist_ok=True)

    content = fetch_page_content(URL)

    if content:
        df = scrape_flats_data(content)
        df = add_pdf_data_to_df(df)
        df = transform_df(df)

        filename = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        file_path = os.path.join(output_dir, filename)

        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        logging.info(f"Data saved to {filename}")
        print(df)


if __name__ == "__main__":
    main()
