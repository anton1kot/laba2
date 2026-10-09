from datetime import datetime

class Stats:

    def __init__(self,stata=None) -> None:
        if not stata:
            self.first_point = datetime.fromisoformat("3000-01-01T01:00:00Z")
            self.last_point = datetime.fromisoformat("0001-01-01T00:00:00Z")
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

        self.first_point = min(self.first_point, datetime.fromisoformat(event.timestamp))  #event.timestamp)
        self.last_point = max(self.last_point, datetime.fromisoformat(event.timestamp)) #event.timestamp)
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
            "first_timestamp": self.first_point.isoformat(),
            "last_timestamp": self.last_point.isoformat(),
            "skipped_lines": self.skipped_lines
        }
