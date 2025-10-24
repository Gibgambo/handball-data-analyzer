# Beispiel: scraper.py
import requests, os
from bs4 import BeautifulSoup

def fetch_pdf_links(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = [
        a['href'] for a in soup.find_all('a', href=True)
        if a['href'].endswith('.pdf')
    ]
    return links

def download_pdfs(links, folder="data/raw"):
    os.makedirs(folder, exist_ok=True)
    for link in links:
        filename = os.path.join(folder, link.split("/")[-1])
        with open(filename, "wb") as f:
            f.write(requests.get(link).content)