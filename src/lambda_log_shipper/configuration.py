import os

from lambda_log_shipper.utils import get_logger


def parse_env(env_name: str, default: str) -> str:
    try:
        return os.environ.get(env_name, default)
    except Exception:
        get_logger().exception(f"Unable to parse environment {env_name}. Fallback to default.")
        return default


def parse_env_to_int(env_name: str, default: int) -> int:
    try:
        return int(parse_env(env_name, str(default)))
    except Exception:
        get_logger().exception(f"Unable to parse environment {env_name}. Fallback to default.")
        return default


class Configuration:
    # Min records in a batch. Default 10 (don't send before reaching this amount)
    min_batch_size: int = parse_env_to_int("EXTENSION_LOG_BATCH_SIZE", 1_000)

    # Min batch size in milliseconds. Default 10_000 milliseconds
    min_batch_time: int = parse_env_to_int("EXTENSION_LOG_BATCH_TIME", 10_000) / 1_000
