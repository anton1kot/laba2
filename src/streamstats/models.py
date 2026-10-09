class Event:

    def __init__(self, file_number, line_number, timestamp, level, source, message=None):
        self.timestamp = timestamp
        self.level = level
        self.source = source
        self.message = message
        self.file_number = file_number
        self.line_number = line_number

def jsonl_event(file_number, line_number,file):
    #valid_keys(file)
    return Event(file_number,
                 line_number,
                 file['timestamp'],
                 file['level'],
                 file['source'],
                 file['message'] if 'message' in file else None)
def csv_event(file_number, line_number,file):
    if line_number == 0:
        return None
        #valid_keys(file)
    return Event(file_number,
                 line_number,
                 file[0],
                 file[1],
                 file[2],
                 file[3] if len(file)==4 else None)