import json
import sys

from streamstats.errors import (
    CLIConfigError,
    EmptyFileError,
    EventError,
    FormatError,
    TimeStampError,
)

from .parsers import file_pars
from .report import json_write


class Arguments:
    def __init__(self,argvs):
        if len(argvs)>=1:
            self.mode = argvs[0] # Анализируем или выводим --help
            self.args = argvs[1:] #Принимаем аргументы
        else:
            self.mode = "err"
        self.condition = 'names' # Начальное состояние обработки аргумента - имена файлов
        self.files = []
        self.format = None
        self.output_file = None
        self.skip_invalid_flag = False

def main():
    args = Arguments(sys.argv[1:])
    if args.mode == 'analyze':
        for argue in args.args:
            if argue == '--format':
                args.condition = 'format' # Состояние формат ждёт формат
                continue
            if argue == '--output':
                args.condition = 'output'
                continue
            if argue == '--skip-invalid':
                args.skip_invalid_flag = True
                continue
            if argue[0]=='-' and not '.' in argue: # Если ошибка в имени флага, но не начало файла
                raise CLIConfigError(f'unknown flag <{argue}>')

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
        except EmptyFileError as er:
            sys.stderr.write(f'EmptyFileError: {er}')
            sys.exit(2)
        except EventError as er:
            sys.stderr.write(f'EventError: {er}')
            sys.exit(2)
        except TimeStampError as er:
            sys.stderr.write(f'TimeStampError: {er}')
            sys.exit(2)
        except FormatError as er:
            sys.stderr.write(f'FormatError: {er}')
            sys.exit(2)
        if not args.files:
            raise EmptyFileError('Please, input: "... analyze <file_name> --format ..."')
        if args.format is None:
            raise FormatError('Please indicate format: "... --format csv|jsonl"')
        if args.output_file:
            json_write(stata, args.output_file)
        else:
            sys.stdout.write(json.dumps(stata, ensure_ascii=False, indent=2))#.replace('{','').replace('}',' ').replace(',',' ').replace('"',''))
    elif args.mode == "--help":
        sys.stdout.write("""
Usage:
    python -m streamstats analyze FILE1 FILE2 ... --format csv|jsonl 
        Принимает .jsonl и .csv файлы событий соответсвующие формату:
            timestamp: ISO 8601
            level: DEBUG | INFO | WARNING | ERROR | CRITICAL
            source: непустая строка
            message: строка
        Опции:
            --output FILE.json
                - Вывод статистику в JSON файл
            --skip-invalid
                - Пропуск невалидных строк, вывод WARNING в stderr,
                    подсчёт пропущенных строк в общей статистике
            
    Ошибки:
        EventError: Ввод файла, несоответствующего маске;
        EmptyFileError: Не введено ни одного файла;
        TimeStampError: Неверный формат временных меток;
        FormatError: Отсутсвие --format csv|jsonl либо указание иного формата
        CLIConfigError: Ошибки конфигурации CLI
        """)
    else:
        raise CLIConfigError("To see more information: \n\n\t\t\tpython -m streamstats --help\n\n")
if __name__ == "__main__":
    try:
        main()
    except FormatError as er:
        sys.stderr.write(f'FormatError: {er}')
        sys.exit(2)
    except EmptyFileError as er:
        sys.stderr.write(f'EmptyFileError: {er}')
        sys.exit(2)
    except CLIConfigError as er:
        sys.stderr.write(f'CLIConfigError: {er}')
        sys.exit(2)