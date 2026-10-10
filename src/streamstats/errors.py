"""
неверное событие;
ошибка конфигурации CLI.
"""
class StreamStatsError(Exception):
    """Базовый класс ошибок пакета streamstats."""
    pass

class EventError(StreamStatsError):
    pass

class FormatError(StreamStatsError):
    pass

class TimeStampError(StreamStatsError):
    pass

class CliConfigError(StreamStatsError):
    pass