import csv
import json
import sys
from json import JSONDecodeError

from .analysis import Stats
from .errors import *
from .models import csv_event, jsonl_event


def file_pars(file_format,files_name, skip_invalid_flag):
    stata = Stats()
    for file_number, file_name in enumerate(files_name):
        file_number+=1 # Считаем, номер файла, если вдруг он повреждён
        stata = events(stata, file_format, file_name, file_number, skip_invalid_flag)

    return stata.stat()

def events(stata, file_format,file_name, file_number, skip_invalid_flag):
    stata = Stats(stata)
    line_number = 0
    try:
        if file_format == 'jsonl':
            with open(file_name, 'r', encoding='utf-8') as jsonl_file:
                for line_number, line in enumerate(jsonl_file) :
                    if line == '\n': continue

                    try:
                        stata.analys(jsonl_event(file_number, line_number,json.loads(line.strip())))
                    except TimeStampError as er:
                        if skip_invalid_flag:
                            stata.skipped_lines += 1
                            sys.stderr.write(f'WARNING: line #{line_number}, file #{file_number}\n')
                        else:
                            raise TimeStampError(f'{er} in file {file_number} line {line_number} field "timestamp"')
                    except KeyError as er:
                        if skip_invalid_flag:
                            stata.skipped_lines += 1
                            sys.stderr.write(f'WARNING: line #{line_number}, file #{file_number}\n')
                        else:
                            raise EventError(f'"{type(er).__name__}" in file {file_number}, line {line_number}')
                    except StreamStatsError as er:
                        if skip_invalid_flag:
                            stata.skipped_lines += 1
                            sys.stderr.write(f'WARNING: line #{line_number}, file #{file_number}\n')
                        else:
                            raise EventError(f'"{type(er).__name__}" in file {file_number}, line {line_number}')
                    except JSONDecodeError as er:
                        if skip_invalid_flag:
                            stata.skipped_lines += 1
                            sys.stderr.write(f'WARNING: line #{line_number}, file #{file_number}\n')
                        else:
                            raise EventError(f'"{type(er).__name__}" in file {file_number}, line {line_number}')



        elif file_format == 'csv':
            with open(file_name, encoding="utf-8") as csv_file:
                csv_file = csv.reader(csv_file)
                for line in csv_file:
                    line_number += 1
                    try:
                        stata.analys(csv_event(file_number, line_number,line))
                    except TimeStampError as er:
                        if skip_invalid_flag:
                            stata.skipped_lines += 1
                            sys.stderr.write(f'WARNING: line #{line_number}, file #{file_number}\n')
                        else:
                            raise TimeStampError(f'{er} in file {file_number} line {line_number} field "timestamp"')
                    except KeyError as er:
                        if skip_invalid_flag:
                            stata.skipped_lines += 1
                            sys.stderr.write(f'WARNING: line #{line_number}, file #{file_number}\n')
                        else:
                            raise EventError(f'"{type(er).__name__}" in file {file_number}, line {line_number}')
                    except StreamStatsError as er:
                        if skip_invalid_flag:
                            stata.skipped_lines += 1
                            sys.stderr.write(f'WARNING: line #{line_number}, file #{file_number}\n')
                        else:
                            raise EventError(f'"{type(er).__name__}" in file {file_number}, line {line_number}')

        else: raise FormatError(f'<{file_format}> is unsupported format, only <csv> or <jsonl>')
    except FileNotFoundError as er:
        raise CLIConfigError(f'{type(er).__name__} in file {file_number}')

    return stata
