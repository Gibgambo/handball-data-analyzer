import pdfplumber
import pandas as pd
import os

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

all_games = []

for pdf_file in os.listdir(RAW_DIR):
    if not pdf_file.endswith(".pdf"):
        continue
    pdf_path = os.path.join(RAW_DIR, pdf_file)
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            
            # Einfaches Beispiel: jede Zeile splitten
            for line in text.split("\n"):
                if "Tor" in line:  # Filter für Tore, Beispiel
                    # Annahme: Zeile = "Spielername  Minute  Art"
                    parts = line.split()
                    if len(parts) >= 2:
                        all_games.append({
                            "pdf_file": pdf_file,
                            "player": parts[0],
                            "minute": parts[1],
                            "info": " ".join(parts[2:])  # optional
                        })

# Alle gesammelten Daten in CSV speichern
df = pd.DataFrame(all_games)
csv_path = os.path.join(PROCESSED_DIR, "games.csv")
df.to_csv(csv_path, index=False)
print(f"✅ Alle Daten gespeichert in {csv_path}")
