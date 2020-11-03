from datetime import datetime

import pytest

from lambda_log_shipper.handlers.base_handler import LogType, LogRecord


@pytest.mark.parametrize(
    "record_type, expected",
    [
        ("platform.start", LogType.START),
        ("platform.end", LogType.END),
        ("platform.report", LogType.REPORT),
        ("function", LogType.FUNCTION),
        ("platform.extension", LogType.EXTENSION),
        ("platform.logsSubscription", LogType.EXTENSION),
    ],
)
def test_log_type_parse(record_type, expected):
    assert LogType.parse(record_type) == expected


def test_log_type_parse_unknown():
    with pytest.raises(ValueError):
        LogType.parse("other")


def test_log_record_parse(raw_record):
    record = LogRecord.parse(raw_record)
    assert record.log_type == LogType.START
    assert record.record == '{"requestId": "1-2-3-4", "version": "$LATEST"}'
    assert record.log_time == datetime(2020, 11, 2, 12, 2, 4, 575000)
