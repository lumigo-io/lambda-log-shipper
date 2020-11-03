import time
import http
import json
from unittest.mock import Mock
from http.server import HTTPServer
from io import BytesIO

from lambda_log_shipper.logs_subscriber import (
    wait_for_logs,
    _logs_arrived,
    subscribe_to_logs,
    LogsHttpRequestHandler,
)
from lambda_log_shipper.handlers.base_handler import LogsHandler, LogRecord
from lambda_log_shipper.logs_manager import LogsManager


def test_wait_for_logs_avoiding_timeout(monkeypatch, caplog):
    monkeypatch.setattr(time, "time", lambda: 1900)
    wait_for_logs(2000)
    assert len([r for r in caplog.records if r.levelname == "ERROR"]) == 1


def test_wait_for_logs_happy_flow(monkeypatch, caplog):
    _logs_arrived.set()
    monkeypatch.setattr(_logs_arrived, "wait", lambda _: None)
    monkeypatch.setattr(_logs_arrived, "clear", lambda: None)
    wait_for_logs(time.time() * 1000 + 5000)
    assert not [r for r in caplog.records if r.levelname == "ERROR"]


def test_subscribe_to_logs(monkeypatch):
    mock = Mock()
    monkeypatch.setattr(http.client, "HTTPConnection", mock)
    monkeypatch.setattr(HTTPServer, "serve_forever", lambda: None)
    monkeypatch.setattr(HTTPServer, "server_bind", lambda _: None)

    subscribe_to_logs("eid")

    expected = '{"destination": {"protocol": "HTTP", "URI": "http://sandbox:1060"}, "types": ["platform", "function"]}'
    mock("127.0.0.1").request.assert_called_once_with(
        "PUT",
        "/2020-08-15/logs",
        expected,
        headers={"Lambda-Extension-Identifier": "eid"},
    )


def test_do_POST(monkeypatch, raw_record):
    class MockRequest:
        def makefile(self, *args, **kwargs):
            return BytesIO(b"POST /")

        def sendall(self, _):
            pass

    handler = LogsHttpRequestHandler(MockRequest(), ("0.0.0.0", 8888), Mock())
    monkeypatch.setattr(handler, "headers", {"Content-Length": "1000"}, False)
    monkeypatch.setattr(
        handler, "rfile", BytesIO(b"[" + json.dumps(raw_record).encode() + b"]"), False
    )
    handler.do_POST()

    assert LogsManager.get_manager().pending_logs == [LogRecord.parse(raw_record)]
