import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run_cli(args, cwd=None):
    #Запускает CLI и возвращает (stdout, stderr, returncode).
    cmd = [sys.executable, "-m", "streamstats", "analyze"] + args
    result = subprocess.run(
        cmd,
        check=False,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout, result.stderr, result.returncode

def test_cli_single_csv_produces_valid_json():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        file_path = tmp_path / "data.csv"
        content = (
            "timestamp,level,source,message\n"
            "2024-01-01T10:00:00Z,INFO,app,msg1\n"
            "2024-01-01T11:00:00+02:00,ERROR,db,msg2\n"
            "2024-01-01T12:00:00Z,WARNING,net,msg3\n"
        )
        file_path.write_text(content, encoding="utf-8")

        # Передаем ТОЛЬКО файлы и флаги. "analyze" уже внутри run_cli
        stdout, stderr, code = run_cli([str(file_path), "--format", "csv"])

        assert code == 0
        assert stderr == ""
        stats = json.loads(stdout)

        assert "total_events" in stats
        assert stats["total_events"] == 3
        assert stats["by_level"]["INFO"] == 1
        assert stats["by_level"]["ERROR"] == 1
        assert stats["by_level"]["WARNING"] == 1


# 2. CLI: несколько файлов одного формата → единая статистика
def test_cli_multiple_files_same_format():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        csv_path1 = tmp_path / "events1.csv"
        csv_content1 = (
            "timestamp,level,source,message\n"
            "2024-01-01T10:00:00Z,INFO,app,msg1\n"
            "2024-01-01T11:00:00+02:00,ERROR,db,msg2\n"
        )
        csv_path1.write_text(csv_content1, encoding="utf-8")

        csv_path2 = tmp_path / "events2.csv"
        csv_content2 = (
            "timestamp,level,source,message\n"
            "2024-01-01T12:00:00Z,WARNING,net,msg3\n"
            "2024-01-01T13:00:00Z,ERROR,db,msg4\n"
        )
        csv_path2.write_text(csv_content2, encoding="utf-8")
        stdout, stderr, code = run_cli([
            str(csv_path1),
            str(csv_path2),
            "--format", "csv"
        ])

        assert stderr == ''
        assert code == 0
        stats = json.loads(stdout)
        assert stats["total_events"] == 4
        assert stats["by_level"]["INFO"] == 1
        assert stats["by_level"]["ERROR"] == 2
        assert stats["by_level"]["WARNING"] == 1


# 3. CLI: --skip-invalid с файлами перед форматом
def test_cli_skip_invalid_with_files_first():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        file_path = tmp_path / "bad.csv"
        content = (
            "timestamp,level,source,message\n"
            "2024-01-01T10:00:00Z,INFO,a,ok1\n"
            "bad-date,ERROR,b,bad1\n"  # ошибка (невалидная дата)
            "2024-01-01T12:00:00Z,WARNING,c,ok2\n"
        )
        file_path.write_text(content, encoding="utf-8")
        stdout, _stderr, code = run_cli([
            str(file_path),
            "--format", "csv",
            "--skip-invalid"
        ])

        assert code == 0
        stats = json.loads(stdout)
        assert stats["total_events"] == 2  # ok1 и ok2

        # Проверяем, что поле skipped_lines существует и > 0
        assert stats.get("skipped_lines", 0) >= 1


# 4. CLI: вывод в файл
def test_cli_output_to_file_files_first():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "data.csv"
        output_path = tmp_path / "report.json"
        input_path.write_text(
            "timestamp,level,source,message\n"
            "2024-01-01T10:00:00Z,INFO,app,msg1\n"
            "2024-01-01T11:00:00Z,ERROR,db,msg2\n",
            encoding="utf-8",
        )
        stdout, stderr, code = run_cli([
            str(input_path),
            "--format", "csv",
            "--output", str(output_path)
        ])
        assert stderr == ""
        assert code == 0
        assert stdout == ""  # При использовании --output stdout должен быть пустым
        assert output_path.exists()

        report = json.loads(output_path.read_text(encoding="utf-8"))
        assert report["total_events"] == 2
        assert report["by_level"]["INFO"] == 1
        assert report["by_level"]["ERROR"] == 1
