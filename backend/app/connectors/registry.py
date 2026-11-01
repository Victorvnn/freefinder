import json
import os
from pathlib import Path

def load_sources():
    return json.loads(Path(os.getenv('SOURCES_FILE',Path(__file__).resolve().parents[2]/'sources.json')).read_text(encoding='utf-8'))
