class Event:

    def __init__(self, file_number: str, timestamp: str, level: str, source: str, message=None) -> None:
        self.timestamp = timestamp
        self.level = level
        self.source = source
        self.message = message
        self.file_number = file_number

def jsonl_event(num,file):
    #valid_keys(file)
    return Event(num,
                 file['timestamp'],
                 file['level'],
                 file['source'],
                 file['message'] if 'message' in file else None)