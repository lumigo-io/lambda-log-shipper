import json
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Union

from lambda_log_shipper.configuration import Configuration
from lambda_log_shipper.utils import get_logger


class LogType(Enum):
    START = "START"
    END = "END"
    REPORT = "REPORT"
    FUNCTION = "FUNCTION"
    EXTENSION = "EXTENSION"

    @staticmethod
    def parse(record_type):
        if record_type == "platform.start":
            return LogType.START
        elif record_type == "platform.end":
            return LogType.END
        elif record_type == "platform.report":
            return LogType.REPORT
        elif record_type == "function":
            return LogType.FUNCTION
        elif record_type in ("platform.logsSubscription", "platform.extension"):
            return LogType.EXTENSION
        raise ValueError("Unknown record type")


@dataclass(frozen=True)
class LogRecord:
    log_type: LogType
    log_time: datetime
    record: str

    @staticmethod
    def parse(record: Dict[str, str]) -> "LogRecord":
        return LogRecord(
            log_type=LogType.parse(record["type"]),
            log_time=datetime.fromisoformat(record["time"][:-1]),
            record=json.dumps(record["record"]),
        )


class LogsHandler:
    _singleton = None

    def __init__(self):
        self.last_sent_time: datetime = datetime.now()
        self.pending_logs: List[LogRecord] = []

    @staticmethod
    def handle_logs(records: List[LogRecord]):
        raise NotImplementedError()

    def add_records(self, raw_records: List[dict]) -> bool:
        new_records = [LogRecord.parse(r) for r in raw_records]
        self.pending_logs.extend(new_records)
        big_batch = len(self.pending_logs) >= Configuration.min_batch_size
        old_batch = (
            datetime.now() - self.last_sent_time
        ).total_seconds() >= Configuration.min_batch_time
        if big_batch or old_batch:
            self.send_batch()
            return True
        return False

    def send_batch(self):
        self.last_sent_time = datetime.now()
        sorted_logs = sorted(self.pending_logs, key=lambda r: r.log_time)
        self.pending_logs.clear()
        subclasses = LogsHandler.__subclasses__()
        get_logger().debug(f"Send logs to handlers: {[c.__name__ for c in subclasses]}")
        for cls in subclasses:
            try:
                cls.handle_logs(sorted_logs)
            except Exception:
                get_logger().exception(
                    f"Exception while handling {cls.__name__}", exc_info=True
                )
            else:
                get_logger().debug(f"{cls.__name__} finished successfully")

    @staticmethod
    def get_handler():
        if not LogsHandler._singleton:
            LogsHandler._singleton = LogsHandler()
        return LogsHandler._singleton
