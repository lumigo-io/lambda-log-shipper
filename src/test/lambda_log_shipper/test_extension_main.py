import http
import time
from types import SimpleNamespace
import urllib
from unittest.mock import Mock

from lambda_log_shipper.extension_main import register_extension, extension_loop


def test_register_happy_flow(monkeypatch):
    mock = Mock()
    mock("127.0.0.1").getresponse.return_value = SimpleNamespace(
        headers={"Lambda-Extension-Identifier": "eid"}, read=lambda: ""
    )
    monkeypatch.setattr(http.client, "HTTPConnection", mock)
    result = register_extension()

    assert result == "eid"


def test_extension_loop_happy_flow(monkeypatch):
    """
    This test checks the case of two requests and shutdown.
    """
    deadline = time.time() * 1000
    http_mock = Mock()
    http_mock.read.side_effect = [
        f'{{"eventType": "INVOKE", "requestId": "1", "deadlineMs": {deadline}}}',
        f'{{"eventType": "INVOKE", "requestId": "2", "deadlineMs": {deadline}}}',
        f'{{"eventType": "SHUTDOWN", "deadlineMs": {deadline}}}',
    ]
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args: http_mock)

    extension_loop("eid")  # finishes successfully

    assert http_mock.read.call_count == 3
