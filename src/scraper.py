import os
import requests
import re
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URL der Liga-Seite
BASE_URL = "https://hvnb-handball.liga.nu"
START_URL = (
    "https://hvnb-handball.liga.nu/cgi-bin/WebObjects/nuLigaHBDE.woa/wa/groupPage?"
    "displayTyp=vorrunde&displayDetail=meetings&championship=HVNB+25%2F26&group=431976"
)

# Zielordner für PDFs
DOWNLOAD_DIR = "../data/raw"

def fetch_pdf_links(url):
    """Lädt die Liga-Seite und extrahiert alle PDF-Links."""
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    pdf_links = []
    
    # Finde alle <a> Tags mit class="picto-pdf"
    for a_tag in soup.find_all("a", class_="picto-pdf"):
        relative_link = a_tag.get("href")
        full_link = urljoin(BASE_URL, relative_link)
        pdf_links.append(full_link)
    
    return pdf_links


def download_pdfs(links, folder=DOWNLOAD_DIR):
    """Lädt alle PDFs aus der Liste herunter."""
    os.makedirs(folder, exist_ok=True)
    
    for link in links:
        file_name = safe_filename_from_url(link)
        file_path = os.path.join(folder, file_name)
        
        print(f"Lade herunter: {file_name}")
        response = requests.get(link)
        response.raise_for_status()
        
        with open(file_path, "wb") as f:
            f.write(response.content)
    
    print(f"\n✅ {len(links)} PDFs wurden in '{folder}' gespeichert.")

def safe_filename_from_url(url):
    """Erzeugt einen sicheren Dateinamen aus der URL."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    # Falls 'meeting' vorhanden, nimm das
    if 'meeting' in query:
        name = query['meeting'][0]
    # sonst nimm alles nach 'dokument=' oder fallback
    elif 'dokument' in query:
        name = query['dokument'][0]
    else:
        name = os.path.basename(parsed.path)

    # Entferne verbotene Zeichen
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    return name + ".pdf"

if __name__ == "__main__":
    pdf_links = fetch_pdf_links(START_URL)
    print(f"Gefundene PDF-Links: {len(pdf_links)}")
    for link in pdf_links[:3]:
        print(link)
    
    download_pdfs(pdf_links)
