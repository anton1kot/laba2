import json
from .models import jsonl_event, csv_event
from .analysis import Stats

def file_pars(file_format,files_name):
    file_number = 0
    stata = Stats()
    for file_name in files_name:
        file_number+=1
        stata = events(stata, file_format, file_name, file_number)
    return stata.stat()

def events(stata, file_format,file_name, file_number):
    stata = Stats(stata)
    line_number = 0
    if file_format == 'jsonl':
        with open(file_name, 'r', encoding='utf-8') as jsonl_file:
            for line in jsonl_file:
                line_number += 1
                stata.analys(jsonl_event(file_number, line_number,json.loads(line.strip())))
    if file_format == 'csv':
        line_number -= 1
        with open(file_name, encoding="utf-8") as csv_file:
            for line in csv_file:
                line_number += 1
                line=line.split(',')
                stata.analys(csv_event(file_number, line_number,line))


    return stata
