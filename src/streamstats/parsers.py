import json
from laba2.src.streamstats.models import jsonl_event
from src.streamstats.analysis import Stats
from src.streamstats.models import Event

'''
def events(file_format, event):
    if file_format == 'csv':
'''
def events(file_format,file_name):
    stata = Stats()
    num=0
    if file_format == 'jsonl':
        num+=1
        with open(file_name, 'r', encoding='utf-8') as jsonl_file:
            for line in jsonl_file:
                stata.analys(jsonl_event(num,json.loads(line.strip())))
    return stata.stat()