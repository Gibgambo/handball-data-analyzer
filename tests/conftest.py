import sys
from pathlib import Path

# Die Module in src/ importieren sich gegenseitig ohne Paketpräfix
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
