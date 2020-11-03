from typing import List
import random

import boto3

from lambda_log_shipper.handlers.base_handler import LogsHandler, LogRecord
from lambda_log_shipper.configuration import Configuration
from lambda_log_shipper.utils import get_logger


class S3Handler(LogsHandler):
    @staticmethod
    def handle_logs(records: List[LogRecord]) -> bool:
        get_logger().debug(f"S3Handler got {records}")
        if Configuration.s3_bucket_arn and records:
            s3 = boto3.client("s3")
            key = S3Handler.generate_key_name(records)
            file_data = S3Handler.format_records(records)
            s3.put_object(Body=file_data, Bucket=Configuration.s3_bucket_arn, Key=key)
            return True
        return False

    @staticmethod
    def generate_key_name(records: List[LogRecord]):
        t = min(r.log_time for r in records)
        return f"logs/{t.year}/{t.month}/{t.day}/{t.hour}/{t.minute}:{t.second}:{t.microsecond}-{random.random()}"

    @staticmethod
    def format_records(records: List[LogRecord]) -> bytes:
        return "\n".join(
            f"{r.log_time.isoformat()}-{r.record}" for r in records
        ).encode()
