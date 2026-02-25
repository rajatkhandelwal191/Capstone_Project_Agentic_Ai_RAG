import json
from pathlib import Path

def load_prompts():
    path = Path(__file__).parent / "prompts.json"
    with open(path) as f:
        return json.load(f)