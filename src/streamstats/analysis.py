

class Stats:

    def __init__(self) -> None:
        self.first_point = 2030
        self.last_point = 0
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


    def analys(self,event):
        time = event.timestamp
        time = int(time[:3] + time[15])
        self.first_point = min(self.first_point, time)  #event.timestamp)
        self.last_point = max(self.last_point, time) #event.timestamp)
        self.level_count[event.level] += 1
        if event.source in self.source_count:
            self.source_count[event.source] += 1
        else:
            self.source_count[event.source] = 1
        if event.level in ('ERROR', 'CRITICAL'):
            if event.source in self.bad_source_count:
                self.bad_source_count[event.source] += 1
            else:
                self.bad_source_count[event.source] = 1

        self.count = sum(self.source_count.values())
        sorted_bad_source = dict(sorted(self.bad_source_count.items(), key=lambda x: x, reverse=True))
        first_five_source=list(sorted_bad_source)[:5]
        self.top_bad_source = {}
        for i in first_five_source:
            self.top_bad_source[i] = sorted_bad_source[i]

    def stat(self):
        return {
            "total_events": self.count,
            "by_level": self.level_count,
            "by_source": self.source_count,
            "top_5_error_sources": self.top_bad_source,
            "first_timestamp": self.first_point,
            "last_timestamp": self.last_point,
            "skipped_lines": self.skipped_lines
        }