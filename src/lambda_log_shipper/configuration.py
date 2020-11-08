import os
from typing import Optional

from lambda_log_shipper.utils import get_logger


def parse_env(env_name: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(env_name, default)


def parse_env_to_int(env_name: str, default: int) -> int:
    try:
        return int(parse_env(env_name) or default)
    except Exception:
        get_logger().exception(
            f"Unable to parse environment {env_name}. Fallback to default."
        )
        return default


class Configuration:
    # Min batch size. Default 1KB (don't send before reaching this amount)
    min_batch_size: int = parse_env_to_int("LUMIGO_EXTENSION_LOG_BATCH_SIZE", 1_000)

    # Min batch size in milliseconds. Default 1 minute
    min_batch_time: float = (
        parse_env_to_int("LUMIGO_EXTENSION_LOG_BATCH_TIME", 60_000) / 1_000
    )

    # Destination S3 bucket to write the logs. Default None to not publish to S3.
    s3_bucket_arn: Optional[str] = parse_env("LUMIGO_EXTENSION_LOG_S3_BUCKET", None)
