
class StreamStatsError(Exception):
    #Базовый класс ошибок пакета streamstats.
    pass

class EmptyFileError(StreamStatsError):
    pass

class EventError(StreamStatsError):
    pass

class EmptySourceError(EventError):
    # Пустой источник, разновидность ошибки события
    pass

class FormatError(StreamStatsError):
    pass

class TimeStampError(StreamStatsError):
    pass

class CLIConfigError(StreamStatsError):
    # Ошибка конфигурации CLI
    pass