#Laba2

## Потоковый анализатор файлов событий

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
        EmptyFileError: Пустой файл или не введено ни одного файла;
        TimeStampError: Неверный формат временных меток;
        FormatError: Отсутсвие --format csv|jsonl либо указание иного формата
        CLIConfigError: 
