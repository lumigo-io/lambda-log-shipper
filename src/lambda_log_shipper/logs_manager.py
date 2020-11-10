from datetime import datetime
from typing import List

from lambda_log_shipper.handlers.base_handler import LogRecord, LogsHandler
from lambda_log_shipper.configuration import Configuration
from lambda_log_shipper.utils import get_logger


class LogsManager:
    _singleton = None

    def __init__(self):
        self.last_sent_time: datetime = datetime.now()
        self.pending_logs: List[LogRecord] = []
        self.pending_logs_size: int = 0

    def add_records(self, raw_records: List[dict]):
        new_records = [LogRecord.parse(r) for r in raw_records]
        self.pending_logs.extend(new_records)
        self.pending_logs_size += sum((len(r.record) for r in new_records), 0)

    def send_batch_if_needed(self):
        big_batch = self.pending_logs_size >= Configuration.min_batch_size
        old_batch = (
            datetime.now() - self.last_sent_time
        ).total_seconds() >= Configuration.min_batch_time
        if big_batch or old_batch:
            self.send_batch()
            return True
        return False

    def send_batch(self) -> bool:
        self.last_sent_time = datetime.now()
        if not self.pending_logs:
            return False
        sorted_logs = sorted(self.pending_logs, key=lambda r: r.log_time)
        self.pending_logs.clear()
        self.pending_logs_size = 0
        subclasses = LogsHandler.__subclasses__()
        get_logger().debug(f"Send logs to handlers: {[c.__name__ for c in subclasses]}")
        for cls in subclasses:
            try:
                cls().handle_logs(sorted_logs)  # type: ignore
            except Exception:
                get_logger().exception(
                    f"Exception while handling {cls.__name__}", exc_info=True
                )
            else:
                get_logger().debug(f"{cls.__name__} finished successfully")
        return True

    @staticmethod
    def get_manager():
        if not LogsManager._singleton:
            LogsManager._singleton = LogsManager()
        return LogsManager._singleton
