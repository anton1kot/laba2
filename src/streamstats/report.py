from .parsers import file_pars
import json

def json_write(file_format,file_name):
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(file_pars(file_format, file_name), f, indent=2, ensure_ascii=False)
