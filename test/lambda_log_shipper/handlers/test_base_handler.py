from datetime import datetime

import pytest

from lambda_log_shipper.handlers.base_handler import LogType, LogRecord, LogsHandler
from lambda_log_shipper.configuration import Configuration


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


def test_log_record_parse(raw_record):
    record = LogRecord.parse(raw_record)
    assert record.log_type == LogType.START
    assert record.record == '{"requestId": "1-2-3-4", "version": "$LATEST"}'
    assert record.log_time == datetime(2020, 11, 2, 12, 2, 4, 575000)


def test_send_batch_some_failures(caplog, record):
    class TestHandler(LogsHandler):
        @staticmethod
        def handle_logs(records):
            1 / 0

    handler = LogsHandler()
    handler.pending_logs.append(record)
    handler.send_batch()  # No exception

    assert len([r for r in caplog.records if r.levelname == "ERROR"]) == 1
    assert [r for r in caplog.records if r.levelname == "DEBUG"]


def test_add_records_no_send():
    assert not LogsHandler().add_records([])


def test_add_records_big_batch(raw_record):
    assert LogsHandler().add_records([raw_record] * (Configuration.min_batch_size + 1))


def test_add_records_old_batch(raw_record, monkeypatch):
    monkeypatch.setattr(Configuration, "min_batch_time", -1)
    assert LogsHandler().add_records([raw_record])


def test_send_batch_empty():
    assert not LogsHandler().send_batch()
