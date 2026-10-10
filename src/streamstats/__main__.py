'''

jsonl
../../../f2.jsonl

Задачи:
    - объединить файлы в начале parsers.py
    - счётчик плохих линий
    - обработка ошибок (через класс)
CLI:
    - ввод
    - хелп
    - вывод ошибок (из класса)
    -


'''
import json
import sys
from logging import raiseExceptions

from streamstats.errors import StreamStatsError, EventError, TimeStampError, FormatError
from .report import json_write
from .parsers import file_pars

class Arguments:
    def __init__(self,argvs):
        if len(argvs)>=1:
            self.mode = argvs[0]
            self.args = argvs[1:]
        else:
            self.mode = "err"
        self.condition = 'names'
        self.files = []
        self.format = None
        self.output_file = None
        self.skip_invalid_flag = False

def main():
    args = Arguments(sys.argv[1:])
    if args.mode == 'analyze':
        for argue in args.args:
            if argue == '--format':
                args.condition = 'format'
                continue
            if argue == '--output':
                args.condition = 'output'
                continue
            if argue == '--skip-invalid': args.skip_invalid_flag = True
            if args.condition == 'names':
                args.files.append(argue)
            if args.condition == 'format':
                args.format = argue
                args.condition = None
            if args.condition == 'output':
                args.output_file = argue
                args.condition = None
    try:
        stata = file_pars(args.format, args.files, args.skip_invalid_flag)
    except EventError as er:
        sys.stderr.write(f'EventError: {er}')
        sys.exit(2)
#    except TimeStampError as er:
        sys.stderr.write(f'TimeStampError: {er}')
        sys.exit(2)
    except FormatError as er:
        sys.stderr.write(f'FormatError: {er}')
        sys.exit(2)
    if args.output_file:
        json_write(stata)
    else:
        sys.stdout.write(json.dumps(stata, ensure_ascii=False, indent=2).replace('{','').replace('}',' ').replace(',',' ').replace('"',''))


if __name__ == "__main__":

    main()