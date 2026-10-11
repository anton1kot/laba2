import json


def json_write(stata, file):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(stata, f, indent=2, ensure_ascii=False)
