import json
import tempfile
from pathlib import Path

import pytest

from streamstats.errors import CLIConfigError, EventError, FormatError, TimeStampError
from streamstats.parsers import file_pars


def test_jsonl():
    with tempfile.TemporaryDirectory() as dir:
        file_path = Path(dir) / "test.jsonl"

        content = [
            json.dumps({"timestamp": "2024-01-01T10:00:00Z", "level": "INFO", "source": "app", "message": "ok"}) + "\n",
            json.dumps({"timestamp": "2024-01-01T11:00:00+03:00", "level": "ERROR", "source": "db", "message": "fail"}) + "\n",
        ]
        file_path.write_text("".join(content), encoding="utf-8")

        stats = file_pars("jsonl", [str(file_path)], skip_invalid_flag=False)

        assert stats["total_events"] == 2
        assert stats["by_level"]["INFO"] == 1
        assert stats["by_level"]["ERROR"] == 1


def test_csv():
    with tempfile.TemporaryDirectory() as dir:
        file_path = Path(dir) / "unicode.csv"

        content = (
            "timestamp,level,source,message\n"
            "2024-01-01T10:00:00Z,INFO,sour,67\n"
            "2024-01-01T11:00:00Z,WARNING,sour, \n"
        )
        file_path.write_text(content, encoding="utf-8")

        file_pars("csv", [str(file_path)], skip_invalid_flag=False)


def test_jsonl_skip_invalid():
    #Проверяет, что при skip_invalid_flag=True невалидная строка пропускается.
    with tempfile.TemporaryDirectory() as dir:
        file_path = Path(dir) / "bad.jsonl"

        content = [
            json.dumps({"timestamp": "2024-01-01T10:00:00Z", "level": "INFO", "source": "a", "message": "x"}) + "\n",
            "{not valid json\n",  # невалидный JSON
            json.dumps({"timestamp": "2024-01-01T12:00:00Z", "level": "WARNING", "source": "b", "message": "y"}) + "\n",
        ]
        file_path.write_text("".join(content), encoding="utf-8")

        stats = file_pars("jsonl", [str(file_path)], skip_invalid_flag=True)

        # Одна строка пропущена, две обработаны
        assert stats["total_events"] == 2
        assert stats["skipped_lines"] == 1


def test_jsonl_stop_on_invalid():
    #Проверяет, что при skip_invalid_flag=False на первой ошибке выбрасывается исключение.
    with tempfile.TemporaryDirectory() as dir:
        file_path = Path(dir) / "bad.jsonl"

        content = ["{not valid\n"]
        file_path.write_text("".join(content), encoding="utf-8")

        with pytest.raises(EventError):
            file_pars("jsonl", [str(file_path)], skip_invalid_flag=False)


def test_csv_skip_invalid():
    #CSV: две проблемные строки (невалидная дата и неизвестный level).
    #При skip_invalid_flag=True они должны быть пропущены.
    with tempfile.TemporaryDirectory() as dir:
        file_path = Path(dir) / "bad.csv"

        content = (
            "timestamp,level,source,message\n"
            "not-a-date,INFO,app,msg\n"      # плохой timestamp
            "2024-01-01T12:00:00Z,UNKNOWN,x,y\n"  # неизвестный level
        )
        file_path.write_text(content, encoding="utf-8")

        stats = file_pars("csv", [str(file_path)], skip_invalid_flag=True)

        # Обе строки пропущены, событий нет
        assert stats["total_events"] == 0
        assert stats["skipped_lines"] == 2


def test_csv_stop_on_invalid():
    #CSV: при skip_invalid_flag=False на первой ошибке должно быть исключение.
    with tempfile.TemporaryDirectory() as dir:
        file_path = Path(dir) / "bad.csv"

        content = "not-a-date,INFO,app,msg\n"
        file_path.write_text(content, encoding="utf-8")

        with pytest.raises((TimeStampError, EventError)):
            file_pars("csv", [str(file_path)], skip_invalid_flag=False)


def test_unsupported_format():
    #Проверка ошибки на неподдерживаемом формате.
    #Здесь даже не нужен реальный файл — достаточно передать любой путь.
    with tempfile.TemporaryDirectory() as dir:
        file_path = Path(dir) / "file.xls"

        with pytest.raises(FormatError):
            file_pars("xls", [str(file_path)], skip_invalid_flag=False)


def test_file_not_found():
    #Проверка обработки FileNotFoundError (превращается в CLIConfigError).
    # Просто указываем несуществующий путь
    with pytest.raises(CLIConfigError):
        file_pars("csv", ["log67.csv"], skip_invalid_flag=False)


def test_unicode_in_csv():
    #CSV с кириллицей: проверяет, что кодировка UTF-8 работает и данные парсятся.
    with tempfile.TemporaryDirectory() as dir:
        file_path = Path(dir) / "unicode.csv"

        content = (
            "timestamp,level,source,message\n"
            "2024-01-01T10:00:00Z,INFO,какой-то источник,ещкере\n"
            "2024-01-01T11:00:00Z,WARNING,мемность,бурмалда\n"
        )
        file_path.write_text(content, encoding="utf-8")

        stats = file_pars("csv", [str(file_path)], skip_invalid_flag=False)

        assert stats["total_events"] == 2
        assert stats["by_source"]["какой-то источник"] == 1
        assert stats["by_source"]["мемность"] == 1

def test_empty_file_returns_zero_stats():
    # Пустой файл создаёт нулевой отчёт без падения
    with tempfile.TemporaryDirectory() as dir:
        file_path = Path(dir) / "empty.csv"
        file_path.write_text("", encoding="utf-8")

        stats = file_pars("csv", [str(file_path)], skip_invalid_flag=False)

        assert stats["total_events"] == 0
        assert stats["skipped_lines"] == 0
        assert stats["by_level"] == {'CRITICAL': 0, 'DEBUG': 0, 'ERROR': 0, 'INFO': 0, 'WARNING': 0}
        assert "top_5_error_sources" in stats and len(stats["top_5_error_sources"]) == 0

def test_csv_and_jsonl_produce_same_stats():
    #Один файл CSV и эквивалентный JSONL дают одинаковую статистику
    with tempfile.TemporaryDirectory() as dir:
        csv_path = Path(dir) / "data.csv"
        csv_content = (
            "timestamp,level,source,message\n"
            "2024-01-01T10:00:00Z,INFO,app,hello\n"
            "2024-01-01T11:00:00+02:00,ERROR,db,fail\n"
            "2024-01-01T12:00:00Z,WARNING,net,timeout\n"
        )
        csv_path.write_text(csv_content, encoding="utf-8")

        jsonl_path = Path(dir) / "data.jsonl"
        jsonl_lines = [
            json.dumps({"timestamp": "2024-01-01T10:00:00Z", "level": "INFO", "source": "app", "message": "hello"}),
            json.dumps({"timestamp": "2024-01-01T11:00:00+02:00", "level": "ERROR", "source": "db", "message": "fail"}),
            json.dumps({"timestamp": "2024-01-01T12:00:00Z", "level": "WARNING", "source": "net", "message": "timeout"}),
        ]
        jsonl_path.write_text("\n".join(jsonl_lines) + "\n", encoding="utf-8")

        stats_csv = file_pars("csv", [str(csv_path)], skip_invalid_flag=False)
        stats_jsonl = file_pars("jsonl", [str(jsonl_path)], skip_invalid_flag=False)

        assert stats_csv["total_events"] == stats_jsonl["total_events"] == 3
        assert stats_csv["by_level"] == stats_jsonl["by_level"]
        assert stats_csv["top_5_error_sources"] == stats_jsonl["top_5_error_sources"]

def test_multiple_files_aggregate_correctly():
    # Несколько файлов агрегируются без потери событий
    with tempfile.TemporaryDirectory() as dir:
        f1 = Path(dir) / "f1.csv"
        f2 = Path(dir) / "f2.csv"

        f1.write_text("timestamp,level,source,message\n2024-01-01T10:00:00Z,INFO,a,msg1\n", encoding="utf-8")
        f2.write_text("timestamp,level,source,message\n2024-01-01T11:00:00Z,ERROR,b,msg2\n2024-01-01T12:00:00Z,WARNING,c,msg3\n", encoding="utf-8")

        stats = file_pars("csv", [str(f1), str(f2)], skip_invalid_flag=False)

        assert stats["total_events"] == 3
        assert stats["by_level"]["INFO"] == 1
        assert stats["by_level"]["ERROR"] == 1
        assert stats["by_level"]["WARNING"] == 1
