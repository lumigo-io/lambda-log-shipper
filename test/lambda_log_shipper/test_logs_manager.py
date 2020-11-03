from lambda_log_shipper.handlers.base_handler import LogsHandler
from lambda_log_shipper.logs_manager import LogsManager
from lambda_log_shipper.configuration import Configuration


def test_send_batch_some_failures(caplog, record):
    class TestHandler(LogsHandler):
        def handle_logs(self, records):
            1 / 0

    manager = LogsManager()
    manager.pending_logs.append(record)
    manager.send_batch()  # No exception

    assert len([r for r in caplog.records if r.levelname == "ERROR"]) == 1
    assert [r for r in caplog.records if r.levelname == "DEBUG"]


def test_add_records_no_send():
    assert not LogsManager.get_manager().add_records([])


def test_add_records_big_batch(raw_record):
    assert LogsManager.get_manager().add_records(
        [raw_record] * (Configuration.min_batch_size + 1)
    )


def test_add_records_clear_after_send(raw_record):
    assert LogsManager.get_manager().add_records(
        [raw_record] * (Configuration.min_batch_size + 1)
    )
    assert not LogsManager.get_manager().send_batch()


def test_add_records_old_batch(raw_record, monkeypatch):
    monkeypatch.setattr(Configuration, "min_batch_time", -1)
    assert LogsManager.get_manager().add_records([raw_record])


def test_send_batch_empty():
    assert not LogsManager.get_manager().send_batch()
