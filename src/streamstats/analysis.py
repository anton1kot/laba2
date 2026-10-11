from datetime import datetime

from streamstats.errors import TimeStampError


class Stats:

    def __init__(self,stata=None) -> None:
        self.top_bad_source = {}
        if not stata: # Смотрим: создаём или обновляем статистику
            self.first_point = None
            self.last_point = None
            self.level_count = {
                "INFO": 0,
                "DEBUG": 0,
                "WARNING": 0,
                "ERROR": 0,
                "CRITICAL": 0
            }
            self.source_count = {}
            self.bad_source_count = {}
            self.skipped_lines = 0
            self.count = 0
        else:
            self.first_point = stata.first_point
            self.last_point = stata.last_point
            self.level_count = stata.level_count
            self.source_count = stata.source_count
            self.bad_source_count = stata.bad_source_count
            self.skipped_lines = stata.skipped_lines
            self.count = stata.count



    def analys(self,event=None):
        if event == None:
            return 0
        try:
            if self.first_point: # Если есть с чем сравнить
                self.first_point = min(self.first_point, datetime.fromisoformat(event.timestamp))
                self.last_point = max(self.last_point, datetime.fromisoformat(event.timestamp))
            else:
                self.first_point = datetime.fromisoformat(event.timestamp)
                self.last_point = datetime.fromisoformat(event.timestamp)
        except ValueError as er:
            raise TimeStampError(er)
        self.level_count[event.level] += 1 # Считаем в формате LEVEL: count
        if event.source in self.source_count:
            self.source_count[event.source] += 1
        else:
            self.source_count[event.source] = 1 # Создаём новый ключ источника
        if event.level in ('ERROR', 'CRITICAL'):
            if event.source in self.bad_source_count:
                self.bad_source_count[event.source] += 1
            else:
                self.bad_source_count[event.source] = 1

        self.count = sum(self.source_count.values())

    def stat(self):
        # Сортируем по элементам, срезаем первые пять, возвращаем словарем
        self.top_bad_source = dict(sorted(self.bad_source_count.items(), key=lambda x: x[1], reverse=True)[:5])
        return {
            "total_events": self.count,
            "by_level": self.level_count,
            "by_source": self.source_count,
            "top_5_error_sources": self.top_bad_source,
            "first_timestamp": self.first_point.isoformat() if self.first_point else None,
            "last_timestamp": self.last_point.isoformat() if self.first_point else None,
            "skipped_lines": self.skipped_lines
        }
