from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
from enum import Enum
import json


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


class LogsHandler(ABC):
    @abstractmethod
    def handle_logs(self, records: List[LogRecord]):
        raise NotImplementedError()
