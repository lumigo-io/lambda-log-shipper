from typing import List

from lambda_log_shipper.handlers.base_handler import LogsHandler, LogRecord
from lambda_log_shipper.utils import get_logger


class S3Handler(LogsHandler):
    @staticmethod
    def handle_logs(records: List[LogRecord]):
        get_logger().debug(f"S3Handler got {records}")
