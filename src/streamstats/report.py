from .parsers import file_pars
import json

def json_write(stata):
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(stata, f, indent=2, ensure_ascii=False)
