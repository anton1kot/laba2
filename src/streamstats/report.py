from laba2.src.streamstats.parsers import events
import json

file_format = input()
file_name = input()
stata = events(file_format, file_name)

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(stata, f, indent=2, ensure_ascii=False)
